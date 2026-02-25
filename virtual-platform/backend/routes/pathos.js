/**
 * PaTHos API Routes
 * 
 * This module defines the REST API endpoints for the PaTHos system.
 * All routes require both authentication and a valid license key.
 * 
 * Base Path: /api/pathos
 * Authentication: Required (JWT Token)
 * License: Required (X-License-Key header)
 */

const express = require('express');
const router = express.Router();
const authMiddleware = require('../middleware/auth');
const licenseMiddleware = require('../middleware/license');

// Apply authentication and license validation to all PaTHos routes
router.use(authMiddleware);
router.use(licenseMiddleware);

/**
 * Execute a PaTHos Function
 * 
 * @route POST /api/pathos/execute
 * @param {string} req.body.functionName - Name of the function to execute
 * @param {*} req.body.input - Input data for the function
 * @param {*} [req.body.expectedOutput] - Optional expected output for validation
 * @returns {Object} JSON object containing:
 *   - success: Boolean indicating execution success
 *   - result: Function execution result
 *   - module: Name of the executed module
 * @throws {400} If function name or input is missing
 * @throws {404} If requested module is not found
 * @throws {500} For server errors during execution
 */
router.post('/execute', async (req, res) => {
  try {
    const { functionName, input, expectedOutput } = req.body;

    // Validate required fields
    if (!functionName || !input) {
      return res.status(400).json({ 
        message: 'Function name and input are required' 
      });
    }

    // Try to load the requested module
    try {
      const module = require(`../modules/${functionName}`);
      
      // Execute the module's function
      const result = await module.execute(input);

      // Compare with expected output if provided
      if (expectedOutput && JSON.stringify(result) !== JSON.stringify(expectedOutput)) {
        return res.status(400).json({
          message: 'Output does not match expected result',
          expected: expectedOutput,
          actual: result
        });
      }

      res.json({
        success: true,
        result,
        module: functionName
      });
    } catch (moduleError) {
      return res.status(404).json({
        message: `Module '${functionName}' not found or failed to execute`,
        error: moduleError.message
      });
    }
  } catch (error) {
    console.error('PaTHos execution error:', error);
    res.status(500).json({ 
      message: 'Error executing PaTHos function',
      error: error.message 
    });
  }
});

/**
 * List Available PaTHos Modules
 * 
 * @route GET /api/pathos/modules
 * @returns {Object} JSON object containing:
 *   - modules: Array of available module names
 * @throws {500} If error occurs while retrieving module list
 * 
 * Note: In production, this would dynamically list available modules
 * rather than returning a static list.
 */
router.get('/modules', (req, res) => {
  try {
    // Group modules by their categories
    const modules = {
      nlp: {
        sentiment: {
          name: 'Sentiment Analysis',
          description: 'Analyzes text for sentiment and emotional content'
        }
      },
      development: {
        mercury: {
          name: 'Mercury',
          description: 'Generates unit tests for code modules'
        },
        venus: {
          name: 'Venus',
          description: 'Performs automated regression testing'
        },
        earth: {
          name: 'Earth',
          description: 'Generates foundational code structures'
        },
        mars: {
          name: 'Mars',
          description: 'Identifies security vulnerabilities'
        },
        jupiter: {
          name: 'Jupiter',
          description: 'Analyzes and documents code'
        }
      },
      ai: {
        ceres: {
          name: 'Ceres',
          description: 'Chatbot development and integration'
        },
        eris: {
          name: 'Eris',
          description: 'Speech recognition and synthesis'
        },
        haumea: {
          name: 'Haumea',
          description: 'Image and video processing'
        }
      },
      infrastructure: {
        neptune: {
          name: 'Neptune',
          description: 'Data visualization and reporting'
        },
        pluto: {
          name: 'Pluto',
          description: 'Knowledge graph management'
        }
      }
    };

    res.json({ 
      modules,
      // For backward compatibility, provide a flat list of module keys
      availableModules: ['sentiment', ...Object.values(modules)
        .flatMap(category => Object.keys(category))]
    });
  } catch (error) {
    console.error('Error listing modules:', error);
    res.status(500).json({ 
      message: 'Error retrieving available modules',
      error: error.message 
    });
  }
});

module.exports = router;
