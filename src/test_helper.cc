#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include <exception>
#include <iostream>
#include <nlohmann/json.hpp>
#include <vector>

#include "c++17.hpp"

using json = nlohmann::json;

namespace {
void call_cmd(std17::string_view cmd_name, const char *path,
              std::vector<std17::string_view> &read_cmd_names,
              std::vector<std17::string_view> &edit_cmd_names)
{
#define READ_ACTION(CMD_NAME)                          \
    if ((read_cmd_names.push_back(#CMD_NAME), true) && \
        (read_cmd_names.back() == cmd_name))
#define EDIT_ACTION(CMD_NAME)                          \
    if ((edit_cmd_names.push_back(#CMD_NAME), true) && \
        (edit_cmd_names.back() == cmd_name))

    struct stat statbuf;
    struct stat64 stat64buf;

    READ_ACTION(stat) stat(path, &statbuf);
    READ_ACTION(lstat) lstat(path, &statbuf);
    READ_ACTION(stat64) stat64(path, &stat64buf);

    READ_ACTION(fopen_r) fopen(path, "r");
    EDIT_ACTION(fopen_rp) fopen(path, "r+");
    EDIT_ACTION(fopen_w) fopen(path, "w");
    EDIT_ACTION(fopen_wp) fopen(path, "w+");
    EDIT_ACTION(fopen_a) fopen(path, "a");
    EDIT_ACTION(fopen_ap) fopen(path, "a+");
    // TODO: test Glibc extensions for mode

    READ_ACTION(open_rdonly) open(path, O_RDONLY);
    EDIT_ACTION(open_wdonly) open(path, O_WRONLY);
    EDIT_ACTION(open_rdwr) open(path, O_RDWR);

    // TODO: creat
    //
    // TODO: test creation (i.e. path does not point to existing file)

    READ_ACTION(openat_rdonly) openat(AT_FDCWD, path, O_RDONLY);
    EDIT_ACTION(openat_wdonly) openat(AT_FDCWD, path, O_WRONLY);
    EDIT_ACTION(openat_rdwr) openat(AT_FDCWD, path, O_RDWR);

    // TODO: test openat when dir is not AT_FDCWD
    //
    // TODO: test the *64 calls

    EDIT_ACTION(unlink) unlink(path);
    EDIT_ACTION(unlinkat) unlinkat(AT_FDCWD, path, 0);

    READ_ACTION(access) access(path, F_OK);
    READ_ACTION(faccessat) faccessat(AT_FDCWD, path, F_OK, 0);

    // TODO: test rename (calls with two paths)
}

struct arg_list {
    arg_list(int argc, const char *argv[]) : argc(argc), argv(argv) {}

    std17::string_view pop_string()
    {
        if (i >= argc) {
            throw std::runtime_error("invalid argument");
        }
        return argv[i++];
    }

    void finalize()
    {
        if (i != argc) {
            throw std::runtime_error("invalid argument");
        }
    }

private:
    int i = 1, argc;
    const char **argv;
};

void main_(int argc, const char *argv[])
{
    arg_list args(argc, argv);

    bool getcmds(argc == 1);
    std17::string_view cmd(getcmds ? "" : args.pop_string());
    std17::string_view path(getcmds ? "." : args.pop_string());
    args.finalize();

    std::vector<std17::string_view> read_cmd_names;
    std::vector<std17::string_view> edit_cmd_names;
    call_cmd(cmd, path.data(), read_cmd_names, edit_cmd_names);

    if (getcmds) {
        std::string stat_data(json{
            {"readcmds", read_cmd_names},
            {"editcmds",
             edit_cmd_names}}.dump());
        std::cout << stat_data << std::endl;
    }
}
}  // namespace

int main(int argc, const char *argv[])
{
    try {
        main_(argc, argv);
    } catch (std::runtime_error &ex) {
        std::cerr << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
