
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface ActiveTaskProps {
  task: {
    title: string;
    description: string;
    duration: string;
    restrictions?: string;
  } | null;
  timeRemaining?: number;
  startTime?: Date;
}

export const ActiveTask: React.FC<ActiveTaskProps> = ({ 
  task, 
  timeRemaining = 0, 
  startTime 
}) => {
  if (!task) {
    return (
      <Card className="w-full h-[250px] flex items-center justify-center">
        <CardContent className="text-center text-gray-400">
          <p>No active task. Create a new task to get started.</p>
        </CardContent>
      </Card>
    );
  }

  const totalDuration = parseInt(task.duration, 10) * 60; // convert to seconds
  const progress = Math.max(0, Math.min(100, ((totalDuration - timeRemaining) / totalDuration) * 100));
  
  // Format time remaining as MM:SS
  const formatTimeRemaining = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="w-full shadow-md border-l-4 border-l-kiddogreen">
      <CardHeader>
        <CardTitle className="text-2xl text-kiddogreen-dark">{task.title}</CardTitle>
        <CardDescription>
          {startTime ? `Started at ${startTime.toLocaleTimeString()}` : 'Task ready to start'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {task.description && (
          <div className="text-gray-700">
            <p>{task.description}</p>
          </div>
        )}
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{formatTimeRemaining(timeRemaining)} remaining</span>
          </div>
          <Progress value={progress} className="h-2 bg-gray-200" />
        </div>
      </CardContent>
    </Card>
  );
};
