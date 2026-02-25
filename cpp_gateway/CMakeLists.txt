cmake_minimum_required(VERSION 3.16)
project(gateway CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Simple HTTP server without external dependencies
add_executable(gateway main.cpp)
find_package(Threads REQUIRED)
target_link_libraries(gateway PRIVATE Threads::Threads)
