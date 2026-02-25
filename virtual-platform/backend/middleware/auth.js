/**
 * Authentication Middleware
 * 
 * This middleware validates JWT tokens for protected routes.
 * It extracts the token from the Authorization header and verifies
 * its authenticity using the JWT_SECRET environment variable.
 * 
 * Usage:
 * ```
 * router.use(authMiddleware); // Protect all routes
 * // or
 * router.get('/protected', authMiddleware, (req, res) => {}); // Protect single route
 * ```
 * 
 * Required Headers:
 * - Authorization: Bearer <token>
 * 
 * Environment Variables:
 * - JWT_SECRET: Secret key for JWT verification
 */

const jwt = require('jsonwebtoken');

/**
 * JWT Authentication Middleware
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 * @returns {void}
 * @throws {401} If token is missing or invalid
 * 
 * On successful validation:
 * - Adds decoded user data to req.user
 * - Calls next() to proceed to the next middleware/route handler
 */
const authMiddleware = (req, res, next) => {
  try {
    // Extract JWT token from Authorization header
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({ message: 'No authentication token, authorization denied.' });
    }

    // Verify token authenticity and decode payload
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Attach decoded user data to request object for use in route handlers
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Token is not valid' });
  }
};

module.exports = authMiddleware;
