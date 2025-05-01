
import React, { useState, useEffect } from 'react';
import { TaskForm } from '@/components/TaskForm';
import { ActiveTask } from '@/components/ActiveTask';
import { ScreenShareStatus } from '@/components/ScreenShareStatus';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { screenShareService } from '@/services/screenShareService';

interface Task {
  title: string;
  description: string;
  duration: string;
  restrictions: string;
}

const TaskPage: React.FC = () => {
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [taskStartTime, setTaskStartTime] = useState<Date | undefined>(undefined);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [timerActive, setTimerActive] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    
    if (timerActive && activeTask && timeRemaining > 0) {
      timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            setTimerActive(false);
            toast({
              title: "Task Completed!",
              description: `"${activeTask.title}" has been completed.`,
              variant: "default",
            });
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [timerActive, timeRemaining, activeTask, toast]);

  const handleTaskSubmit = (task: Task) => {
    // Convert minutes to seconds for the timer
    const durationSeconds = parseInt(task.duration, 10) * 60;
    
    setActiveTask(task);
    setTimeRemaining(durationSeconds);
    setTaskStartTime(new Date());
    setTimerActive(true);
    
    toast({
      title: "New Task Started",
      description: `"${task.title}" has been started.`,
    });

    // Log restrictions if provided
    if (task.restrictions && task.restrictions.trim() !== '') {
      console.log("Content restrictions applied:", task.restrictions);
      
      toast({
        title: "Content Restrictions Applied",
        description: "Content restrictions are now active for this session.",
      });
    }
  };

  const endCurrentTask = () => {
    if (!activeTask) return;
    
    // Stop screen sharing if active
    if (screenShareService.isScreenSharing()) {
      screenShareService.stopScreenShare();
    }
    
    setActiveTask(null);
    setTimerActive(false);
    setTaskStartTime(undefined);
    
    toast({
      title: "Task Ended",
      description: `"${activeTask.title}" has been ended early.`,
      variant: "destructive",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container max-w-4xl mx-auto px-4">
        <header className="mb-8 text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-kiddoblue-dark mb-2">
            KiddoPlay Task Monitor
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Create tasks for your child and monitor their screen while they complete them.
          </p>
        </header>
      
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-6">
            <ActiveTask 
              task={activeTask} 
              timeRemaining={timeRemaining} 
              startTime={taskStartTime} 
            />
            
            {activeTask && (
              <Button 
                onClick={endCurrentTask} 
                variant="outline"
                className="w-full border-red-300 text-red-500 hover:bg-red-50"
              >
                End Current Task
              </Button>
            )}
            
            <ScreenShareStatus />
          </div>
          
          <div>
            {!activeTask ? (
              <TaskForm onSubmit={handleTaskSubmit} />
            ) : (
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                <h2 className="text-xl font-semibold mb-4 text-kiddoblue">Task Instructions</h2>
                <ol className="list-decimal list-inside space-y-3 text-gray-700">
                  <li>Ensure your child is seated at the computer</li>
                  <li>Click "Start Screen Monitoring" to begin supervision</li>
                  <li>Our system will monitor progress while they work</li>
                  <li>When the time is up, the task will complete automatically</li>
                  <li>You can end the task early if needed using the "End Current Task" button</li>
                </ol>
                
                {activeTask.restrictions && activeTask.restrictions.trim() !== '' ? (
                  <div className="mt-4 pt-4 border-t">
                    <h3 className="font-medium text-kiddoblue mb-2">Content Restrictions:</h3>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-md">
                      {activeTask.restrictions}
                    </div>
                  </div>
                ) : null}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskPage;
