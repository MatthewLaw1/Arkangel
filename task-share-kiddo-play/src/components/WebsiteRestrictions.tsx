
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

export interface WebsiteRestriction {
  id: string;
  name: string;
  enabled: boolean;
}

export interface CustomRestriction {
  id: string;
  url: string;
}

interface WebsiteRestrictionsProps {
  onRestrictionsChange: (restrictions: WebsiteRestriction[], customRestrictions: CustomRestriction[]) => void;
}

export const WebsiteRestrictions: React.FC<WebsiteRestrictionsProps> = ({ onRestrictionsChange }) => {
  const [restrictions, setRestrictions] = useState<WebsiteRestriction[]>([
    { id: 'social-media', name: 'Social Media (Facebook, Instagram, TikTok, etc.)', enabled: false },
    { id: 'games', name: 'Games Websites', enabled: false },
    { id: 'video', name: 'Video Platforms (YouTube, Twitch, etc.)', enabled: false },
  ]);
  
  const [customRestrictions, setCustomRestrictions] = useState<CustomRestriction[]>([]);
  const [newCustomUrl, setNewCustomUrl] = useState('');

  const handleRestrictionToggle = (id: string) => {
    setRestrictions(prev => {
      const updated = prev.map(restriction => 
        restriction.id === id 
          ? { ...restriction, enabled: !restriction.enabled } 
          : restriction
      );
      onRestrictionsChange(updated, customRestrictions);
      return updated;
    });
  };

  const addCustomRestriction = () => {
    if (!newCustomUrl.trim()) return;
    
    const newRestriction = {
      id: `custom-${Date.now()}`,
      url: newCustomUrl.trim()
    };
    
    setCustomRestrictions(prev => {
      const updated = [...prev, newRestriction];
      onRestrictionsChange(restrictions, updated);
      return updated;
    });
    
    setNewCustomUrl('');
  };

  const removeCustomRestriction = (id: string) => {
    setCustomRestrictions(prev => {
      const updated = prev.filter(item => item.id !== id);
      onRestrictionsChange(restrictions, updated);
      return updated;
    });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-kiddoblue dark:text-kiddoblue-light">Website Restrictions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h3 className="text-md font-medium">Block Access To:</h3>
          
          {restrictions.map((restriction) => (
            <div key={restriction.id} className="flex items-start space-x-2">
              <Checkbox 
                id={restriction.id}
                checked={restriction.enabled} 
                onCheckedChange={() => handleRestrictionToggle(restriction.id)} 
              />
              <Label 
                htmlFor={restriction.id}
                className="text-sm font-normal leading-tight cursor-pointer"
              >
                {restriction.name}
              </Label>
            </div>
          ))}
        </div>

        <div className="space-y-2 pt-2 border-t">
          <h3 className="text-md font-medium">Custom Restricted Websites:</h3>
          
          <div className="flex items-center space-x-2">
            <Input
              placeholder="Enter website URL (e.g., roblox.com)"
              value={newCustomUrl}
              onChange={(e) => setNewCustomUrl(e.target.value)}
              className="flex-grow"
            />
            <Button onClick={addCustomRestriction} type="button" size="sm">
              Add
            </Button>
          </div>
          
          <div className="space-y-2 mt-2">
            {customRestrictions.map((item) => (
              <div key={item.id} className="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                <span className="text-sm truncate flex-1">{item.url}</span>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => removeCustomRestriction(item.id)}
                  className="h-8 w-8"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
