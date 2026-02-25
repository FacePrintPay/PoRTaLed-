import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();

  // Function to check if a link is active
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-gray-800 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between">
          <div className="flex space-x-7">
            {/* Logo */}
            <div>
              <Link to="/" className="flex items-center py-4">
                <span className="font-semibold text-white text-lg">Virtual Platform</span>
              </Link>
            </div>

            {/* Primary Nav */}
            <div className="hidden md:flex items-center space-x-1">
              <Link
                to="/"
                className={`py-4 px-2 ${
                  isActive('/') 
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Home
              </Link>
              <Link
                to="/meetings"
                className={`py-4 px-2 ${
                  isActive('/meetings')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Meetings
              </Link>
              <Link
                to="/concerts"
                className={`py-4 px-2 ${
                  isActive('/concerts')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Concerts
              </Link>
              <Link
                to="/shopping"
                className={`py-4 px-2 ${
                  isActive('/shopping')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Shopping
              </Link>
              <Link
                to="/art"
                className={`py-4 px-2 ${
                  isActive('/art')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Art
              </Link>
              <Link
                to="/payments"
                className={`py-4 px-2 ${
                  isActive('/payments')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Payments
              </Link>
              <Link
                to="/enterprise"
                className={`py-4 px-2 ${
                  isActive('/enterprise')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                Enterprise
              </Link>
              <Link
                to="/pathos"
                className={`py-4 px-2 ${
                  isActive('/pathos')
                    ? 'text-green-500 border-b-4 border-green-500'
                    : 'text-gray-300 hover:text-green-500 transition duration-300'
                }`}
              >
                PaTHos
              </Link>
            </div>
          </div>

          {/* Secondary Nav */}
          <div className="hidden md:flex items-center space-x-3">
            <Link
              to="/login"
              className={`py-2 px-4 ${
                isActive('/login')
                  ? 'bg-green-500 text-white'
                  : 'text-gray-300 hover:text-green-500 transition duration-300'
              }`}
            >
              Login
            </Link>
            <Link
              to="/register"
              className={`py-2 px-4 ${
                isActive('/register')
                  ? 'bg-green-500 text-white'
                  : 'bg-green-500 text-white hover:bg-green-600 transition duration-300 rounded'
              }`}
            >
              Register
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button className="outline-none mobile-menu-button">
              <svg
                className="w-6 h-6 text-gray-300 hover:text-green-500"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
