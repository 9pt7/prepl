add_library(pwatch SHARED pwatch.cc)
target_compile_features(pwatch PUBLIC cxx_std_20)
target_link_libraries(pwatch dl nlohmann_json)
add_custom_command(TARGET pwatch POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
  $<TARGET_FILE:pwatch>
  ${PROJECT_SOURCE_DIR}/pwatch
  )
