add_library(pwatch SHARED pwatch.cc)
target_compile_features(pwatch PUBLIC cxx_std_17)
target_link_libraries(pwatch dl nlohmann_json)
add_custom_command(TARGET pwatch POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
  $<TARGET_FILE:pwatch>
  ${PROJECT_SOURCE_DIR}/pwatch
  )

add_executable(test_helper test_helper.cc)
target_compile_features(test_helper PUBLIC cxx_std_17)
target_link_libraries(test_helper nlohmann_json)
add_custom_command(TARGET test_helper POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
  $<TARGET_FILE:test_helper>
  ${PROJECT_SOURCE_DIR}/tests
  )
