import { claudeService } from './claudeService';

/**
 * Service for managing screen sharing functionality
 */
export class ScreenShareService {
  private stream: MediaStream | null = null;
  private isSharing = false;
  
  /**
   * Request screen sharing permissions from the user
   * @returns Promise resolving to a boolean indicating success
   */
  async requestScreenShare(): Promise<boolean> {
    try {
      this.stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false,
      });
      
      this.isSharing = true;
      
      // Start the Claude monitoring when screen sharing starts
      try {
        await claudeService.startMonitoring();
        console.log("Claude monitoring started successfully");
      } catch (error) {
        console.error("Failed to start Claude monitoring:", error);
        // Continue screen sharing even if monitoring fails
      }
      
      // Handle when user stops sharing via browser UI
      this.stream.getVideoTracks()[0].addEventListener('ended', () => {
        this.stopScreenShare();
      });
      
      return true;
    } catch (error) {
      console.error("Error requesting screen share:", error);
      return false;
    }
  }
  
  /**
   * Stop screen sharing
   */
  stopScreenShare(): void {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
      this.isSharing = false;
      
      // Stop Claude monitoring when screen sharing stops
      try {
        claudeService.stopMonitoring().catch(error => {
          console.error("Error stopping Claude monitoring:", error);
        });
      } catch (error) {
        console.error("Failed to stop Claude monitoring:", error);
      }
    }
  }
  
  /**
   * Check if screen is currently being shared
   */
  isScreenSharing(): boolean {
    return this.isSharing;
  }
  
  /**
   * Get the current screen share stream
   */
  getStream(): MediaStream | null {
    return this.stream;
  }
}

// Create a singleton instance
export const screenShareService = new ScreenShareService();
