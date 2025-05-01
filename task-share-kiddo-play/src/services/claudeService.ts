/**
 * Service for interacting with the Claude API through the Python backend
 */
export class ClaudeService {
    private baseUrl: string = 'http://localhost:5000/api';
    private monitoringActive: boolean = false;
  
    /**
     * Get the latest analysis from Claude
     * @returns Promise with the analysis result
     */
    async getLatestAnalysis() {
      try {
        const response = await fetch(`${this.baseUrl}/analysis`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
      } catch (error) {
        console.error("Error fetching Claude analysis:", error);
        throw error;
      }
    }
  
    /**
     * Get the current task being monitored
     * @returns Promise with the current task
     */
    async getCurrentTask() {
      try {
        const response = await fetch(`${this.baseUrl}/task`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data.task;
      } catch (error) {
        console.error("Error fetching current task:", error);
        throw error;
      }
    }
  
    /**
     * Update the current task being monitored
     * @param task The new task to monitor
     * @returns Promise with the updated task
     */
    async updateTask(task: string) {
      try {
        const response = await fetch(`${this.baseUrl}/task`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ task }),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error("Error updating task:", error);
        throw error;
      }
    }
  
    /**
     * Get the current content restrictions
     * @returns Promise with the list of content restrictions
     */
    async getContentRestrictions() {
      try {
        const response = await fetch(`${this.baseUrl}/restrictions`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data.restrictions;
      } catch (error) {
        console.error("Error fetching content restrictions:", error);
        throw error;
      }
    }
  
    /**
     * Update the content restrictions
     * @param restrictions List of content items to restrict
     * @returns Promise with the updated restrictions
     */
    async updateContentRestrictions(restrictions: string[]) {
      try {
        const response = await fetch(`${this.baseUrl}/restrictions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ restrictions }),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error("Error updating content restrictions:", error);
        throw error;
      }
    }
  
    /**
     * Start the monitoring process
     * @returns Promise with result
     */
    async startMonitoring() {
      try {
        const response = await fetch(`${this.baseUrl}/monitoring/start`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();
        this.monitoringActive = result.success;
        return result;
      } catch (error) {
        console.error("Error starting monitoring:", error);
        throw error;
      }
    }
  
    /**
     * Stop the monitoring process
     * @returns Promise with result
     */
    async stopMonitoring() {
      try {
        const response = await fetch(`${this.baseUrl}/monitoring/stop`, {
          method: 'POST',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();
        this.monitoringActive = !result.success;
        return result;
      } catch (error) {
        console.error("Error stopping monitoring:", error);
        throw error;
      }
    }
  
    /**
     * Check if monitoring is active
     * @returns Promise with monitoring status
     */
    async isMonitoringActive() {
      try {
        const response = await fetch(`${this.baseUrl}/monitoring/status`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();
        this.monitoringActive = result.active;
        return result.active;
      } catch (error) {
        console.error("Error checking monitoring status:", error);
        return false;
      }
    }
  }
  
  // Create a singleton instance
  export const claudeService = new ClaudeService();