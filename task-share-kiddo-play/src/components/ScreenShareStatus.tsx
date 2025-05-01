
import React, { useEffect, useState } from 'react';
import { screenShareService } from '@/services/screenShareService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScreenShare } from 'lucide-react';

export const ScreenShareStatus = () => {
  const [isSharing, setIsSharing] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);

  useEffect(() => {
    // Check initial state
    setIsSharing(screenShareService.isScreenSharing());
    
    // Cleanup when component unmounts
    return () => {
      if (screenShareService.isScreenSharing()) {
        screenShareService.stopScreenShare();
      }
    };
  }, []);

  const handleRequestScreenShare = async () => {
    setShareError(null);
    const success = await screenShareService.requestScreenShare();
    
    if (success) {
      setIsSharing(true);
    } else {
      setShareError("Screen sharing permission was denied. Please try again.");
      setIsSharing(false);
    }
  };

  const handleStopSharing = () => {
    screenShareService.stopScreenShare();
    setIsSharing(false);
  };

  return (
    <Card className={`w-full ${isSharing ? 'border-kiddogreen' : 'border-gray-300'}`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-lg font-medium">
            Screen Monitoring
          </CardTitle>
          <CardDescription>
            {isSharing 
              ? "Monitoring child's screen activity" 
              : "Monitor your child's screen while they complete the task"}
          </CardDescription>
        </div>
        <div className={`p-2 rounded-full ${isSharing ? 'bg-kiddogreen/20' : 'bg-gray-200'}`}>
          <ScreenShare 
            className={`h-6 w-6 ${isSharing ? 'text-kiddogreen animate-pulse-slow' : 'text-gray-500'}`}
          />
        </div>
      </CardHeader>
      <CardContent>
        {shareError && (
          <p className="text-destructive text-sm mb-3">{shareError}</p>
        )}
        <Button 
          onClick={isSharing ? handleStopSharing : handleRequestScreenShare}
          className={isSharing 
            ? "w-full bg-red-500 hover:bg-red-600 text-white" 
            : "w-full bg-kiddoblue hover:bg-kiddoblue-dark text-white"}
        >
          {isSharing ? "Stop Monitoring" : "Start Screen Monitoring"}
        </Button>
      </CardContent>
    </Card>
  );
};
