/**
 * PaTHos Sentiment Analysis Module
 * 
 * This module provides natural language processing capabilities for sentiment analysis
 * using the 'sentiment' npm package. It analyzes text input and returns detailed
 * sentiment metrics including score, comparative analysis, and token breakdown.
 */

const Sentiment = require('sentiment');
const sentiment = new Sentiment();

module.exports = {
  /**
   * Executes sentiment analysis on the provided text input
   * 
   * @param {string|Object} input - Text to analyze or object containing text field
   * @returns {Object} Analysis results including:
   *   - score: Overall sentiment score
   *   - comparative: Normalized sentiment score
   *   - tokens: Array of tokens analyzed
   *   - words: Object containing positive and negative words found
   *   - positive: Array of positive words
   *   - negative: Array of negative words
   * @throws {Error} If input is invalid or analysis fails
   */
  async execute(input) {
    try {
      // Handle input as either direct text or object with text field
      const text = typeof input === 'object' && input.text ? input.text : input;
      
      // Validate input
      if (!text || typeof text !== 'string') {
        throw new Error('Invalid input: expected a text string or object with text field');
      }

      // Perform sentiment analysis
      const result = sentiment.analyze(text);

      // Return formatted results
      return {
        score: result.score,
        comparative: result.comparative,
        tokens: result.tokens,
        words: {
          positive: result.positive,
          negative: result.negative
        },
        calculation: result.calculation,
        metadata: {
          timestamp: new Date().toISOString(),
          wordCount: result.tokens.length,
          language: 'en' // Default to English for now
        }
      };
    } catch (error) {
      throw new Error(`Sentiment analysis failed: ${error.message}`);
    }
  }
};
