
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

interface TaskFormProps {
  onSubmit: (task: { 
    title: string; 
    description: string; 
    duration: string;
    restrictions: string;
  }) => void;
}

export const TaskForm: React.FC<TaskFormProps> = ({ onSubmit }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('30');
  const [restrictions, setRestrictions] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) return;
    
    onSubmit({
      title,
      description,
      duration,
      restrictions
    });
    
    // Reset form
    setTitle('');
    setDescription('');
    setDuration('30');
    // We don't reset restrictions because parents likely want them to persist between tasks
  };

  return (
    <div className="space-y-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-kiddoblue dark:text-kiddoblue-light">Create New Task</CardTitle>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Task Title</Label>
              <Input
                id="title"
                placeholder="e.g., Math Homework"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="border-kiddoblue-light focus:ring-kiddoblue"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Task Description</Label>
              <Textarea
                id="description"
                placeholder="Describe what your child needs to do..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="min-h-[100px] border-kiddoblue-light focus:ring-kiddoblue"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="duration">Duration (minutes)</Label>
              <Input
                id="duration"
                type="number"
                min="1"
                max="120"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="border-kiddoblue-light focus:ring-kiddoblue"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="restrictions">Content Restrictions</Label>
              <Textarea
                id="restrictions"
                placeholder="Describe what your child should not see or use during this task (e.g., social media, games, specific websites)..."
                value={restrictions}
                onChange={(e) => setRestrictions(e.target.value)}
                className="min-h-[100px] border-kiddoblue-light focus:ring-kiddoblue"
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              type="submit" 
              className="w-full bg-kiddogreen hover:bg-kiddogreen-dark text-white"
            >
              Start Task
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};
