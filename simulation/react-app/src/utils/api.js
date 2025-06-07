/**
 * Core Engine API Utilities
 *
 * This file contains utility functions for interacting with the Core Engine backend API.
 */

/**
 * Send a message to the Core Engine backend
 * 
 * @param {Object} message - The message object to send
 * @param {string} userId - The user ID
 * @param {string|null} sessionId - The session ID (null for new sessions)
 * @returns {Promise<Object>} - The response from the server
 */
export const sendMessage = async (message, userId, sessionId = null) => {
  try {
    const response = await fetch('/api/core-engine/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        user_id: userId,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Get session information
 * 
 * @param {string} sessionId - The session ID
 * @returns {Promise<Object>} - The session information
 */
export const getSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/core-engine/session/${sessionId}`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching session:', error);
    throw error;
  }
};

/**
 * Get all sessions for a user
 * 
 * @param {string} userId - The user ID
 * @returns {Promise<Array>} - Array of session objects
 */
export const getUserSessions = async (userId) => {
  try {
    const response = await fetch(`/api/core-engine/user/${userId}/sessions`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user sessions:', error);
    throw error;
  }
};

/**
 * Set a flag for a session
 * 
 * @param {string} sessionId - The session ID
 * @param {string} flagName - The name of the flag to set
 * @param {boolean} value - The value to set the flag to
 * @returns {Promise<Object>} - The updated session information
 */
export const setSessionFlag = async (sessionId, flagName, value) => {
  try {
    const response = await fetch(`/api/core-engine/flag/${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        flag_name: flagName,
        value
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error setting session flag:', error);
    throw error;
  }
};