/**
 * PaTHos Function Execution Interface
 * 
 * This component provides a user interface for executing PaTHos functions and
 * viewing execution history. It includes:
 * - Function selection from available modules
 * - Input data entry
 * - Optional expected output validation
 * - License key validation
 * - Real-time execution feedback
 * - Historical execution records
 * 
 * @component
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Pathos() {
  // State management for form data, available modules, and execution history
  const [formData, setFormData] = useState({
    functionName: '',
    input: '',
    expectedOutput: '',
    licenseKey: ''
  });
  const [moduleData, setModuleData] = useState({ modules: {}, availableModules: [] });
  const [executionHistory, setExecutionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  /**
   * Fetches the list of available PaTHos modules from the backend API
   * Requires valid authentication token and license key
   * Updates the availableModules state with the fetched list
   */
  useEffect(() => {
    fetchModules();
  }, []);

  /**
   * Retrieves available modules from the backend
   * 
   * @async
   * @function fetchModules
   * @throws {Error} If module fetching fails
   */
  const fetchModules = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/pathos/modules', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'X-License-Key': formData.licenseKey
        }
      });
      setModuleData(response.data);
    } catch (err) {
      setError('Failed to fetch available modules');
      console.error('Error fetching modules:', err);
    }
  };

  /**
   * Handles form input changes
   * Updates formData state and clears any previous error/success messages
   * 
   * @param {Object} e - Event object from form input change
   */
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear any previous messages
    setError(null);
    setSuccess(null);
  };

  /**
   * Handles form submission for function execution
   * 
   * @async
   * @param {Object} e - Form submission event
   * @throws {Error} If function execution fails
   * 
   * Process:
   * 1. Prevents default form submission
   * 2. Sets loading state
   * 3. Attempts to execute function with provided inputs
   * 4. Updates execution history on success
   * 5. Handles and displays any errors
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await axios.post(
        'http://localhost:5000/api/pathos/execute',
        {
          functionName: formData.functionName,
          input: formData.input,
          expectedOutput: formData.expectedOutput ? JSON.parse(formData.expectedOutput) : null
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'X-License-Key': formData.licenseKey
          }
        }
      );

      setSuccess('Function executed successfully!');
      setExecutionHistory([response.data, ...executionHistory]);
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred while executing the function');
      console.error('Execution error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="md:grid md:grid-cols-3 md:gap-6">
        {/* Form Section */}
        <div className="md:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">PaTHos Function Execution</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Function Name Select */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Function Name
                </label>
                <select
                  name="functionName"
                  value={formData.functionName}
                  onChange={handleChange}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 rounded-md"
                  required
                >
                  <option value="">Select a function</option>
                  {Object.entries(moduleData.modules).map(([category, modules]) => (
                    <optgroup key={category} label={category.toUpperCase()}>
                      {Object.entries(modules).map(([key, module]) => (
                        <option key={key} value={key}>
                          {module.name}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>

              {/* Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Input
                </label>
                <textarea
                  name="input"
                  value={formData.input}
                  onChange={handleChange}
                  rows="4"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter input data (JSON format)"
                  required
                />
              </div>

              {/* Expected Output */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Expected Output (Optional)
                </label>
                <textarea
                  name="expectedOutput"
                  value={formData.expectedOutput}
                  onChange={handleChange}
                  rows="4"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter expected output (JSON format)"
                />
              </div>

              {/* License Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  License Key
                </label>
                <input
                  type="text"
                  name="licenseKey"
                  value={formData.licenseKey}
                  onChange={handleChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter your license key"
                  required
                />
              </div>

              {/* Error and Success Messages */}
              {error && (
                <div className="rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error</h3>
                      <div className="mt-2 text-sm text-red-700">{error}</div>
                    </div>
                  </div>
                </div>
              )}

              {success && (
                <div className="rounded-md bg-green-50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-green-800">Success</h3>
                      <div className="mt-2 text-sm text-green-700">{success}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    loading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                  }`}
                >
                  {loading ? 'Executing...' : 'Execute Function'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* History Section */}
        <div className="mt-6 md:mt-0">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Execution History</h3>
            <div className="space-y-4">
              {executionHistory.map((execution, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-md p-4 hover:bg-gray-50"
                >
                  <h4 className="text-sm font-bold text-gray-700">
                    {execution.module || execution.functionName}
                  </h4>
                  <p className="mt-1 text-sm text-gray-600">
                    Result: {JSON.stringify(execution.result)}
                  </p>
                  {execution.outputMatched !== undefined && (
                    <p className="mt-1 text-sm text-gray-600">
                      Output Matched: {execution.outputMatched ? '✅' : '❌'}
                    </p>
                  )}
                </div>
              ))}
              {executionHistory.length === 0 && (
                <p className="text-gray-500 text-sm">No execution history yet</p>
              )}
            </div>
          </div>
        </div>

        {/* PaTHos Agents Section */}
        <div className="mt-8">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">PaTHos Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">Development Agents</h3>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <i className="fas fa-code text-green-600 mt-1 mr-2"></i>
                    <div>
                      <span className="font-medium">Earth:</span>
                      <p className="text-sm text-gray-600">Generates foundational code structures</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-bug text-green-600 mt-1 mr-2"></i>
                    <div>
                      <span className="font-medium">Moon:</span>
                      <p className="text-sm text-gray-600">Identifies and resolves syntax errors</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-tachometer-alt text-green-600 mt-1 mr-2"></i>
                    <div>
                      <span className="font-medium">Sun:</span>
                      <p className="text-sm text-gray-600">Optimizes code performance</p>
                    </div>
                  </li>
                </ul>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">AI & NLP Agents</h3>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <i className="fas fa-brain text-green-600 mt-1 mr-2"></i>
                    <div>
                      <span className="font-medium">Mercury:</span>
                      <p className="text-sm text-gray-600">Natural Language Processing analysis</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-heart text-green-600 mt-1 mr-2"></i>
                    <div>
                      <span className="font-medium">Venus:</span>
                      <p className="text-sm text-gray-600">Sentiment analysis and emotion detection</p>
                    </div>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-shield-alt text-green-600 mt-1 mr-2"></i>
                    <div>
                      <span className="font-medium">Mars:</span>
                      <p className="text-sm text-gray-600">Security vulnerability detection</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-4 text-center">
              <a
                href="/docs/agents.html"
                target="_blank"
                className="inline-flex items-center text-green-600 hover:text-green-700"
              >
                <span>View All Agents</span>
                <i className="fas fa-arrow-right ml-2"></i>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Pathos;
