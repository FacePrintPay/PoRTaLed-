/**
 * License Validation Middleware
 * 
 * This middleware validates the license key provided in request headers
 * against a stored license key. It ensures that only authorized clients
 * with valid licenses can access protected PaTHos endpoints.
 * 
 * Usage:
 * ```
 * router.use(licenseMiddleware); // Protect all routes
 * // or
 * router.get('/protected', licenseMiddleware, (req, res) => {}); // Protect single route
 * ```
 * 
 * Required Headers:
 * - X-License-Key: Valid license key
 * 
 * Configuration:
 * - License key is stored in 'pathos-license.txt' in the project root
 * - File path is resolved relative to the middleware location
 */

const fs = require('fs');
const path = require('path');

/**
 * License Key Validation Middleware
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 * @returns {void}
 * @throws {403} If license key is missing or invalid
 * @throws {500} If license verification process fails
 * 
 * Process:
 * 1. Extracts license key from X-License-Key header
 * 2. Reads stored license key from file
 * 3. Compares provided key with stored key
 * 4. Proceeds if keys match, returns error if they don't
 */
const licenseMiddleware = (req, res, next) => {
  try {
    // Extract license key from request header
    const providedLicenseKey = req.header('X-License-Key');

    if (!providedLicenseKey) {
      return res.status(403).json({ message: 'License key is required' });
    }

    // Read and parse the stored license key from configuration file
    const licensePath = path.join(__dirname, '..', 'pathos-license.txt');
    const storedLicenseKey = fs.readFileSync(licensePath, 'utf8').trim();

    // Validate the provided license key against stored key
    if (providedLicenseKey !== storedLicenseKey) {
      return res.status(403).json({ message: 'Invalid license key' });
    }

    next();
  } catch (error) {
    console.error('License verification error:', error);
    res.status(500).json({ message: 'Error verifying license' });
  }
};

module.exports = licenseMiddleware;
