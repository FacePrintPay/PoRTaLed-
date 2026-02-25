/**
 * PaTHos Controller
 * 
 * Core controller class that manages the PaTHos system functionality including:
 * - Module registration and management
 * - Function execution and validation
 * - Execution history tracking
 * - Performance metrics collection
 * 
 * The controller maintains a registry of available modules and their execution history,
 * allowing for both immediate execution results and historical analysis.
 */

class PathosController {
  constructor() {
    this.modules = new Map();
    this.history = [];
  }

  /**
   * Registers a new module with the PaTHos controller
   * 
   * @param {string} name - The unique identifier for the module
   * @param {Object} moduleInstance - The module instance to register
   * @param {Function} moduleInstance.execute - The module's execution function
   * @throws {Error} If a module with the same name is already registered
   */
  registerModule(name, moduleInstance) {
    if (this.modules.has(name)) {
      throw new Error(`Module ${name} is already registered`);
    }
    this.modules.set(name, moduleInstance);
  }

  /**
   * Executes a module's function with the provided input and validates against expected output
   * 
   * @param {string} functionName - The name of the module to execute
   * @param {*} input - The input data to pass to the module
   * @param {*} [expectedOutput=null] - Optional expected output for validation
   * @returns {Promise<Object>} Execution record containing:
   *   - timestamp: ISO string of execution time
   *   - functionName: Name of the executed module
   *   - input: Input data provided
   *   - result: Execution result
   *   - executionTime: Time taken in milliseconds
   *   - success: Boolean indicating execution success
   *   - expectedOutput: (if provided) The expected output
   *   - outputMatched: (if expected output provided) Boolean indicating if output matched
   * @throws {Error} If module is not found or execution fails
   */
  async executeFunction(functionName, input, expectedOutput = null) {
    // Check if module exists
    if (!this.modules.has(functionName)) {
      throw new Error(`Module ${functionName} not found`);
    }

    try {
      // Get the module and execute
      const module = this.modules.get(functionName);
      const startTime = Date.now();
      const result = await module.execute(input);
      const executionTime = Date.now() - startTime;

      // Create execution record
      const executionRecord = {
        timestamp: new Date().toISOString(),
        functionName,
        input,
        result,
        executionTime,
        success: true
      };

      // Validate against expected output if provided
      if (expectedOutput !== null) {
        const outputMatches = JSON.stringify(result) === JSON.stringify(expectedOutput);
        executionRecord.expectedOutput = expectedOutput;
        executionRecord.outputMatched = outputMatches;
        
        if (!outputMatches) {
          executionRecord.success = false;
          executionRecord.error = 'Output did not match expected result';
        }
      }

      // Store in history
      this.history.push(executionRecord);

      return executionRecord;
    } catch (error) {
      // Log error and store in history
      const errorRecord = {
        timestamp: new Date().toISOString(),
        functionName,
        input,
        error: error.message,
        success: false
      };
      this.history.push(errorRecord);
      throw error;
    }
  }

  /**
   * Retrieves the complete execution history
   * 
   * @returns {Array<Object>} Array of execution records in chronological order
   */
  getHistory() {
    return this.history;
  }

  /**
   * Returns a list of all registered module names
   * 
   * @returns {Array<string>} Array of registered module names
   */
  getAvailableModules() {
    return Array.from(this.modules.keys());
  }

  /**
   * Clears all execution history records
   * Useful for testing or maintaining system performance
   */
  clearHistory() {
    this.history = [];
  }
}

// Create and export a singleton instance of the PathosController
// This ensures only one instance exists throughout the application
const pathosController = new PathosController();
module.exports = pathosController;
