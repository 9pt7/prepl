add_library(pwatch SHARED pwatch.cc)
target_compile_features(pwatch PUBLIC cxx_std_20)
target_link_libraries(pwatch dl nlohmann_json)
