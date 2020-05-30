#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>

#if __has_include(<filesystem>)
#include <filesystem>
namespace fs = std::filesystem;
#elif __has_include(<experimental/filesystem>)
#include <experimental/filesystem>
namespace fs = std::experimental::filesystem;
#endif

#include <iostream>
#include <optional>

#include <memory>
#include <nlohmann/json.hpp>
#include <string_view>
#include <tuple>
#include <cstdarg>

using json = nlohmann::json;

#define NEXT(NAME) ((decltype(&NAME))dlsym(RTLD_NEXT, #NAME))

template<auto f>
struct function;

template<typename ReturnType, typename... Args, ReturnType (*f)(Args...)>
struct function<f> {
    using return_type = ReturnType;
    using arg_types = std::tuple<Args...>;
};

#define WRAP_N(CMD, ARGDECL, ARGLIST, ...) \
    extern "C" {                           \
    function<CMD>::return_type CMD ARGDECL \
    {                                      \
        auto r = NEXT(CMD) ARGLIST;        \
        __VA_ARGS__;                       \
        return r;                          \
    }                                      \
    }

template<auto F, std::size_t I>
using arg_type =
    typename std::tuple_element<I, typename function<F>::arg_types>::type;

#define ARG(CMD, I) arg_type<CMD, I> a##I

#define WRAP_0(CMD, ...) WRAP_N(CMD, (), (), __VA_ARGS__)
#define WRAP_1(CMD, ...) WRAP_N(CMD, (ARG(CMD, 0)), (a0), __VA_ARGS__)
#define WRAP_2(CMD, ...) \
    WRAP_N(CMD, (ARG(CMD, 0), ARG(CMD, 1)), (a0, a1), __VA_ARGS__)
#define WRAP_3(CMD, ...)                                               \
    WRAP_N(CMD, (ARG(CMD, 0), ARG(CMD, 1), ARG(CMD, 2)), (a0, a1, a2), \
           __VA_ARGS__)
#define WRAP_4(CMD, ...)                                              \
    WRAP_N(CMD, (ARG(CMD, 0), ARG(CMD, 1), ARG(CMD, 2), ARG(CMD, 3)), \
           (a0, a1, a2, a3), __VA_ARGS__)
#define WRAP_5(CMD, ...)                                                      \
    WRAP_N(CMD,                                                               \
           (ARG(CMD, 0), ARG(CMD, 1), ARG(CMD, 2), ARG(CMD, 3), ARG(CMD, 4)), \
           (a0, a1, a2, a3, a4), __VA_ARGS__)

static std::string errno_string()
{
    constexpr std::size_t buflen = 80;

    std::unique_ptr<char[]> buf(std::make_unique<char[]>(buflen));
    strerror_r(errno, buf.get(), buflen);

    buf[buflen - 1] = '\0';

    return buf.get();
}

struct os_error : std::runtime_error {
    os_error() : runtime_error(errno_string()) {}
};

template<typename F>
static auto check(F f)
{
    return [f](auto... args) {
        auto res = f(args...);
        if (res < 0) throw os_error();
        return res;
    };
}

template<typename F>
struct call_on_exit {
    template<typename... Args>
    call_on_exit(Args &&... args) : f(std::forward<Args>(args)...)
    {
    }

    ~call_on_exit() { f(); }

    F f;
};

template<typename Arg>
call_on_exit(Arg &&)
    ->call_on_exit<std::remove_reference_t<std::remove_const_t<Arg>>>;

static fs::path path_from_fd(int fd)
{
    if (fd == AT_FDCWD) {
        return fs::current_path();
    }

    std::string proc_fd_path(std::string("/proc/self/fd/") +
                             std::to_string(fd));

    const char *proc_str = proc_fd_path.c_str();

    struct stat sb;
    check(lstat)(proc_str, &sb);  // TODO: don't call?

    ssize_t bufsiz = sb.st_size + 1;

    std::unique_ptr<char[]> buf(std::make_unique<char[]>(bufsiz));

    check(readlink)(proc_str, buf.get(), bufsiz);

    return fs::path(buf.get());
}

static int fifofd = -1;

static void __attribute__((destructor)) close_fifo()
{
    if (fifofd >= 0) {
        close(fifofd);
    }
}

static void notify_(const fs::path &file, bool readonly)
{
    fs::path abs = fs::absolute(file);

    const char *fifo_path = getenv("PWATCH_FIFO");
    if (!fifo_path) return;

    if (fifofd < 0) {
        fifofd = check(NEXT(open))(fifo_path, O_WRONLY);
    }

    std::string value = json{
        {"kind", "openfile"},
        {"path", abs.c_str()},
        {"readonly",
         readonly}}.dump();

    check(dprintf)(fifofd, "%s\n", value.c_str());
}

static void
notify(const char *file, bool readonly, std::optional<int> fd = std::nullopt)
{
    try {
        const fs::path f(file);
        const fs::path path((fd && f.is_relative()) ? (path_from_fd(*fd) / f) : f);
        notify_(path, readonly);
    } catch (const std::exception &ex) {
        std::cerr << "Could not notify file=\"" << file;
        std::cerr << "\", readonly=" << (readonly ? "true" : "false");
        std::cerr << ", fd=";
        if (fd)
            std::cerr << *fd;
        else
            std::cerr << "null";
        std::cerr << ", err=\"" << ex.what() << "\"";
        std::cerr << std::endl;
    }
}

static bool is_reg_file(mode_t mode) { return (mode & S_IFMT) == S_IFREG; }

WRAP_2(creat, if (r >= 0) notify(a0, false);)
WRAP_2(creat64, if (r >= 0) notify(a0, false);)

WRAP_4(__xmknod, if (r >= 0 && is_reg_file(a2)) notify(a1, true);)
WRAP_5(__xmknodat, if (r >= 0 && is_reg_file(a3)) notify(a2, true, a1);)

WRAP_3(__xstat, if (r >= 0 && is_reg_file(a2->st_mode)) notify(a1, true);)
WRAP_3(__xstat64, if (r >= 0 && is_reg_file(a2->st_mode)) notify(a1, true);)
WRAP_5(__fxstatat,
       if (r >= 0 && is_reg_file(a3->st_mode)) notify(a2, true, a1);)
WRAP_5(__fxstatat64,
       if (r >= 0 && is_reg_file(a3->st_mode)) notify(a2, true, a1);)
WRAP_3(__lxstat, if (r >= 0 && is_reg_file(a2->st_mode)) notify(a1, true);)
WRAP_3(__lxstat64, if (r >= 0 && is_reg_file(a2->st_mode)) notify(a1, true);)

WRAP_1(unlink, if (r >= 0) notify(a0, false);)
WRAP_3(unlinkat, if (r >= 0) notify(a1, false, a0);)

WRAP_2(access, if (r >= 0) notify(a0, true);)
WRAP_4(faccessat, if (r >= 0) notify(a1, true, a0);)

static bool fopen_readonly(const char *mode)
{
    std::string_view m(mode);
    return m == "r" || m == "rb";
}

WRAP_2(fopen, if (r != nullptr) notify(a0, fopen_readonly(a1));)
WRAP_2(fopen64, if (r != nullptr) notify(a0, fopen_readonly(a1));)

WRAP_2(rename, if (r >= 0) notify(a0, false), notify(a1, false);)
WRAP_4(renameat, if (r >= 0) notify(a1, false, a0), notify(a3, false, a2);)

static constexpr int ACCESS_MODE_MASK = O_RDONLY | O_WRONLY | O_RDWR;

#define OPEN_WITH_NOTIFY(CMD, ARGDECL, ARGLIST, DIRFD)                       \
    extern "C" {                                                             \
    int CMD ARGDECL                                                          \
    {                                                                        \
        std::va_list __args;                                                 \
        va_start(__args, __oflag);                                           \
        mode_t mode =                                                        \
            (__OPEN_NEEDS_MODE(__oflag)) ? va_arg(__args, mode_t) : 0;       \
        va_end(__args);                                                      \
                                                                             \
        int rc = NEXT(CMD) ARGLIST;                                          \
                                                                             \
        if (rc >= 0)                                                         \
            notify(__file, (__oflag & ACCESS_MODE_MASK) == O_RDONLY, DIRFD); \
        return rc;                                                           \
    }                                                                        \
    }

OPEN_WITH_NOTIFY(open, (const char *__file, int __oflag, ...),
                 (__file, __oflag, mode), std::nullopt)

OPEN_WITH_NOTIFY(open64, (const char *__file, int __oflag, ...),
                 (__file, __oflag, mode), std::nullopt)

OPEN_WITH_NOTIFY(openat, (int __fd, const char *__file, int __oflag, ...),
                 (__fd, __file, __oflag, mode), __fd)

OPEN_WITH_NOTIFY(openat64, (int __fd, const char *__file, int __oflag, ...),
                 (__fd, __file, __oflag, mode), __fd)
