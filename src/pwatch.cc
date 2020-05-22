#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <dlfcn.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#include <stdlib.h>

#include <stdio.h>
#include <stdlib.h>

#include <filesystem>
#include <memory>
#include <string_view>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

#define NEXT(NAME) ((decltype(&NAME))dlsym(RTLD_NEXT, #NAME))

template<typename F>
static auto check(F f)
{
    return [f](auto... args) {
        auto res = f(args...);
        if (res < 0) {
        }
        return res;
    };
}

static unsigned char read_byte(int fd)
{
    unsigned char b;
    for (;;) {
        ssize_t nread = check(read)(fd, &b, 1);
        if (nread == 1) return b;
    }
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

static std::filesystem::path path_from_fd(int fd)
{
    std::string proc_fd_path(std::string("/proc/self/fd/") +
                             std::to_string(fd));

    const char *proc_str = proc_fd_path.c_str();

    struct stat sb;
    check(lstat)(proc_str, &sb);  // TODO: don't call?

    ssize_t bufsiz = sb.st_size + 1;

    std::unique_ptr<char[]> buf(std::make_unique<char[]>(bufsiz));

    check(readlink)(proc_str, buf.get(), bufsiz);

    return std::filesystem::path(buf.get());
}

template<typename Arg>
call_on_exit(Arg&&) -> call_on_exit<std::remove_reference_t<std::remove_const_t<Arg>>>;



static void notify(const std::filesystem::path &file, bool readonly)
{
    std::filesystem::path abs = std::filesystem::absolute(file);

    const char *fifo_path = getenv("PWATCH_FIFO");
    if (!fifo_path) return;

    int fifofd = check(NEXT(open))(fifo_path, O_WRONLY);
    call_on_exit close_fifo([fifofd]() { close(fifofd); });

    std::string value = json{
        {"kind", "openfile"},
        {"path", abs.c_str()},
        {"readonly",
         readonly}}.dump();

    check(dprintf)(fifofd, "%s\n", value.c_str());
}

static void notifyat(int fd, const char *file, bool readonly)
{
    notify(std::filesystem::relative(file, path_from_fd(fd)), readonly);
}


constexpr int ACCESS_MODE_MASK = O_RDONLY | O_WRONLY | O_RDWR;

static bool open_readonly(int flags) { return (flags & ACCESS_MODE_MASK) == O_RDONLY; }

#define OPEN_MODE                                                            \
    va_list __args;                                                          \
    va_start(__args, __oflag);                                               \
    mode_t mode = (__OPEN_NEEDS_MODE(__oflag)) ? va_arg(__args, mode_t) : 0; \
    va_end(__args)

extern "C" {

int open(const char *__file, int __oflag, ...)
{
    notify(__file, open_readonly(__oflag));
    OPEN_MODE;
    return NEXT(open)(__file, __oflag, mode);
}

int open64(const char *__file, int __oflag, ...)
{
    notify(__file, open_readonly(__oflag));
    OPEN_MODE;
    return NEXT(open64)(__file, __oflag, mode);
}

int openat(int __fd, const char *__file, int __oflag, ...)
{
    notifyat(__fd, __file, open_readonly(__oflag));
    OPEN_MODE;
    return NEXT(openat)(__fd, __file, __oflag, mode);
}

int openat64(int __fd, const char *__file, int __oflag, ...)
{
    notifyat(__fd, __file, open_readonly(__oflag));
    OPEN_MODE;
    return NEXT(openat64)(__fd, __file, __oflag, mode);
}

int creat(const char *__file, mode_t __mode)
{
    notify(__file, false);
    return NEXT(creat)(__file, __mode);
}

int creat64(const char *__file, mode_t __mode)
{
    notify(__file, false);
    return NEXT(creat64)(__file, __mode);
}

int __xstat(int __ver, const char *pathname, struct stat *statbuf)
{
    notify(pathname, true);
    return NEXT(__xstat)(__ver, pathname, statbuf);
}

int __xstat64(int __ver, const char *pathname, struct stat64 *statbuf)
{
    notify(pathname, true);
    return NEXT(__xstat64)(__ver, pathname, statbuf);
}

int __xmknod(int __ver, const char *__path, __mode_t __mode, __dev_t *__dev)
{
    return NEXT(__xmknod)(__ver, __path, __mode, __dev);
}

int __xmknod64(int __ver, const char *__path, __mode_t __mode, __dev_t *__dev)
{
    return NEXT(__xmknod64)(__ver, __path, __mode, __dev);
}

FILE *fopen(const char *pathname, const char *mode)
{
    std::string_view m(mode);
    notify(pathname, m == "r" || m == "rb");
    return NEXT(fopen)(pathname, mode);
}

FILE *fopen64(const char *pathname, const char *mode)
{
    std::string_view m(mode);
    notify(pathname, m == "r" || m == "rb");
    return NEXT(fopen64)(pathname, mode);
}

int unlink(const char *pathname)
{
    int rc = NEXT(unlink)(pathname);
    if (rc == 0) {
        notify(pathname, false);
    }
    return rc;
}

int unlinkat(int dirfd, const char *pathname, int flags)
{
    int rc = NEXT(unlinkat)(dirfd, pathname, flags);
    if (rc == 0) {
        notifyat(dirfd, pathname, false);
    }
    return rc;
}

int access(const char *pathname, int mode)
{
    notify(pathname, true);
    return NEXT(access)(pathname, mode);
}

int accessat(int dirfd, const char *pathname, int mode, int flags)
{
    notifyat(dirfd, pathname, true);
    return NEXT(accessat)(dirfd, pathname, mode, flags);
}

int rename(const char *oldpath, const char *newpath)
{
    notify(oldpath, true);
    int rc = NEXT(rename)(oldpath, newpath);
    if (rc == 0) {
        notify(newpath, false);
    }
    return rc;
}

int renameat(int olddirfd, const char *oldpath, int newdirfd,
             const char *newpath)
{
    notifyat(olddirfd, oldpath, true);
    int rc = NEXT(renameat)(olddirfd, oldpath, newdirfd, newpath);
    if (rc == 0) {
        notifyat(newdirfd, newpath, false);
    }
    return rc;
}

int renameat2(int olddirfd, const char *oldpath, int newdirfd,
              const char *newpath, unsigned int flags)
{
    notifyat(olddirfd, oldpath, true);
    int rc = NEXT(renameat2)(olddirfd, oldpath, newdirfd, newpath, flags);
    if (rc == 0) {
        notifyat(newdirfd, newpath, false);
    }
    return rc;
}
}
