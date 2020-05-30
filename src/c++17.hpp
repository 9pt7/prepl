#ifndef CPP17_HPP
#define CPP17_HPP

#if __has_include(<filesystem>)
#include <filesystem>
#elif __has_include(<experimental/filesystem>)
#include <experimental/filesystem>
#endif

#if __has_include(<optional>)
#include <optional>
#elif __has_include(<experimental/optional>)
#include <experimental/optional>
#endif

#if __has_include(<string_view>)
#include <string_view>
#elif __has_include(<experimental/string_view>)
#include <experimental/string_view>
#endif

namespace std {
namespace experimental {

}
}  // namespace std

namespace std17 {
using namespace std;
using namespace std::experimental;
}  // namespace std17

#endif
