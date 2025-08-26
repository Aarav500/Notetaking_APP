import React, { useState } from 'react';
import { Calendar, Clock, BellRing, ArrowLeft, Plus, Trash, Check, Calendar as CalendarIcon, Download } from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for topics
const MOCK_TOPICS = [
  { id: 1, name: 'Machine Learning Basics', estimatedHours: 10, difficulty: 'medium' },
  { id: 2, name: 'Neural Networks', estimatedHours: 15, difficulty: 'hard' },
  { id: 3, name: 'Data Preprocessing', estimatedHours: 5, difficulty: 'easy' },
  { id: 4, name: 'Model Evaluation', estimatedHours: 8, difficulty: 'medium' },
  { id: 5, name: 'Deep Learning', estimatedHours: 20, difficulty: 'hard' },
];

// Mock data for generated study plan
const MOCK_STUDY_PLAN = {
  startDate: new Date(),
  endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
  sessions: [
    {
      id: 1,
      topic: 'Machine Learning Basics',
      date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
      duration: 2,
      type: 'initial',
    },
    {
      id: 2,
      topic: 'Machine Learning Basics',
      date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
      duration: 1,
      type: 'review',
    },
    {
      id: 3,
      topic: 'Data Preprocessing',
      date: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000),
      duration: 2,
      type: 'initial',
    },
    {
      id: 4,
      topic: 'Machine Learning Basics',
      date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      duration: 1,
      type: 'review',
    },
    {
      id: 5,
      topic: 'Data Preprocessing',
      date: new Date(Date.now() + 8 * 24 * 60 * 60 * 1000),
      duration: 1,
      type: 'review',
    },
    {
      id: 6,
      topic: 'Neural Networks',
      date: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000),
      duration: 3,
      type: 'initial',
    },
    {
      id: 7,
      topic: 'Machine Learning Basics',
      date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
      duration: 1,
      type: 'review',
    },
    {
      id: 8,
      topic: 'Neural Networks',
      date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000),
      duration: 2,
      type: 'review',
    },
    {
      id: 9,
      topic: 'Data Preprocessing',
      date: new Date(Date.now() + 16 * 24 * 60 * 60 * 1000),
      duration: 1,
      type: 'review',
    },
    {
      id: 10,
      topic: 'Model Evaluation',
      date: new Date(Date.now() + 18 * 24 * 60 * 60 * 1000),
      duration: 2,
      type: 'initial',
    },
  ],
};

const StudyPlanner = ({ onBack }) => {
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [availableTopics, setAvailableTopics] = useState(MOCK_TOPICS);
  const [studyPlan, setStudyPlan] = useState(null);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [showCalendarIntegration, setShowCalendarIntegration] = useState(false);
  const [showReminderSettings, setShowReminderSettings] = useState(false);
  const [calendarType, setCalendarType] = useState('google');
  const [reminderTypes, setReminderTypes] = useState(['email']);
  const [planSettings, setPlanSettings] = useState({
    startDate: new Date(),
    endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    hoursPerWeek: 10,
    includeWeekends: false,
  });
  
  const handleTopicSelect = (topic) => {
    setSelectedTopics([...selectedTopics, topic]);
    setAvailableTopics(availableTopics.filter(t => t.id !== topic.id));
  };
  
  const handleTopicRemove = (topic) => {
    setSelectedTopics(selectedTopics.filter(t => t.id !== topic.id));
    setAvailableTopics([...availableTopics, topic]);
  };
  
  const handlePlanSettingChange = (setting, value) => {
    setPlanSettings({
      ...planSettings,
      [setting]: value,
    });
  };
  
  const handleReminderTypeToggle = (type) => {
    if (reminderTypes.includes(type)) {
      setReminderTypes(reminderTypes.filter(t => t !== type));
    } else {
      setReminderTypes([...reminderTypes, type]);
    }
  };
  
  const generateStudyPlan = async () => {
    if (selectedTopics.length === 0) return;
    
    setIsGeneratingPlan(true);
    
    try {
      // In a real implementation, this would be an API call
      // await api.post('/planner/generate-plan', { topics: selectedTopics, settings: planSettings });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Use mock data for now
      setStudyPlan(MOCK_STUDY_PLAN);
    } catch (error) {
      console.error('Error generating study plan:', error);
    } finally {
      setIsGeneratingPlan(false);
    }
  };
  
  const exportToCalendar = (type) => {
    if (!studyPlan) return;
    
    // In a real implementation, this would generate a calendar file or redirect to a calendar API
    console.log(`Exporting to ${type} calendar`);
    alert(`Study plan would be exported to ${type} calendar in a real implementation.`);
  };
  
  const setupReminders = () => {
    if (!studyPlan) return;
    
    // In a real implementation, this would set up reminders via the selected channels
    console.log(`Setting up reminders via: ${reminderTypes.join(', ')}`);
    alert(`Reminders would be set up via ${reminderTypes.join(', ')} in a real implementation.`);
  };
  
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };
  
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  const getSessionTypeStyle = (type) => {
    switch (type) {
      case 'initial':
        return 'bg-blue-100 text-blue-800';
      case 'review':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Study Planner</h1>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Select Topics</h2>
          
          <div className="border rounded-md p-4 mb-4">
            <h3 className="text-md font-medium mb-3">Selected Topics</h3>
            {selectedTopics.length > 0 ? (
              <div className="space-y-2">
                {selectedTopics.map(topic => (
                  <div key={topic.id} className="flex items-center justify-between p-2 bg-muted/20 rounded-md">
                    <div>
                      <span className="font-medium">{topic.name}</span>
                      <div className="flex items-center text-sm text-muted-foreground mt-1">
                        <Clock className="h-3 w-3 mr-1" />
                        <span>{topic.estimatedHours} hours</span>
                        <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${getDifficultyColor(topic.difficulty)}`}>
                          {topic.difficulty}
                        </span>
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleTopicRemove(topic)}
                    >
                      <Trash className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-4">
                No topics selected. Select topics from the list below.
              </p>
            )}
          </div>
          
          <div className="border rounded-md p-4">
            <h3 className="text-md font-medium mb-3">Available Topics</h3>
            {availableTopics.length > 0 ? (
              <div className="space-y-2">
                {availableTopics.map(topic => (
                  <div 
                    key={topic.id} 
                    className="flex items-center justify-between p-2 hover:bg-muted/20 rounded-md cursor-pointer"
                    onClick={() => handleTopicSelect(topic)}
                  >
                    <div>
                      <span className="font-medium">{topic.name}</span>
                      <div className="flex items-center text-sm text-muted-foreground mt-1">
                        <Clock className="h-3 w-3 mr-1" />
                        <span>{topic.estimatedHours} hours</span>
                        <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${getDifficultyColor(topic.difficulty)}`}>
                          {topic.difficulty}
                        </span>
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTopicSelect(topic);
                      }}
                    >
                      <Plus className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-4">
                No more topics available.
              </p>
            )}
          </div>
        </div>
        
        <div>
          <h2 className="text-lg font-semibold mb-4">Plan Settings</h2>
          
          <div className="border rounded-md p-4 mb-4">
            <div className="space-y-4">
              <div>
                <label htmlFor="startDate" className="block text-sm font-medium mb-1">Start Date</label>
                <input
                  type="date"
                  id="startDate"
                  value={planSettings.startDate.toISOString().split('T')[0]}
                  onChange={(e) => handlePlanSettingChange('startDate', new Date(e.target.value))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              
              <div>
                <label htmlFor="endDate" className="block text-sm font-medium mb-1">End Date</label>
                <input
                  type="date"
                  id="endDate"
                  value={planSettings.endDate.toISOString().split('T')[0]}
                  onChange={(e) => handlePlanSettingChange('endDate', new Date(e.target.value))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              
              <div>
                <label htmlFor="hoursPerWeek" className="block text-sm font-medium mb-1">Hours per Week</label>
                <input
                  type="number"
                  id="hoursPerWeek"
                  min="1"
                  max="40"
                  value={planSettings.hoursPerWeek}
                  onChange={(e) => handlePlanSettingChange('hoursPerWeek', parseInt(e.target.value))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includeWeekends"
                  checked={planSettings.includeWeekends}
                  onChange={(e) => handlePlanSettingChange('includeWeekends', e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="includeWeekends" className="text-sm">Include weekends in study plan</label>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end mb-4">
            <Button
              onClick={generateStudyPlan}
              disabled={isGeneratingPlan || selectedTopics.length === 0}
            >
              {isGeneratingPlan ? (
                <>
                  <div className="animate-spin mr-2">
                    <Calendar className="h-4 w-4" />
                  </div>
                  Generating...
                </>
              ) : (
                <>
                  <Calendar className="h-4 w-4 mr-1" />
                  Generate Study Plan
                </>
              )}
            </Button>
          </div>
          
          {studyPlan && (
            <div className="border rounded-md p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-md font-medium">Study Plan</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowCalendarIntegration(!showCalendarIntegration)}
                  >
                    <CalendarIcon className="h-4 w-4 mr-1" />
                    Calendar
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowReminderSettings(!showReminderSettings)}
                  >
                    <BellRing className="h-4 w-4 mr-1" />
                    Reminders
                  </Button>
                </div>
              </div>
              
              {showCalendarIntegration && (
                <div className="mb-4 p-3 bg-muted/20 rounded-md">
                  <h4 className="font-medium mb-2">Calendar Integration</h4>
                  <div className="flex gap-2 mb-3">
                    <Button
                      variant={calendarType === 'google' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setCalendarType('google')}
                    >
                      Google Calendar
                    </Button>
                    <Button
                      variant={calendarType === 'ical' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setCalendarType('ical')}
                    >
                      iCal
                    </Button>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => exportToCalendar(calendarType)}
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Export to {calendarType === 'google' ? 'Google Calendar' : 'iCal'}
                  </Button>
                </div>
              )}
              
              {showReminderSettings && (
                <div className="mb-4 p-3 bg-muted/20 rounded-md">
                  <h4 className="font-medium mb-2">Reminder Settings</h4>
                  <div className="space-y-2 mb-3">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="emailReminder"
                        checked={reminderTypes.includes('email')}
                        onChange={() => handleReminderTypeToggle('email')}
                        className="mr-2"
                      />
                      <label htmlFor="emailReminder" className="text-sm">Email reminders</label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="discordReminder"
                        checked={reminderTypes.includes('discord')}
                        onChange={() => handleReminderTypeToggle('discord')}
                        className="mr-2"
                      />
                      <label htmlFor="discordReminder" className="text-sm">Discord reminders</label>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={setupReminders}
                    disabled={reminderTypes.length === 0}
                  >
                    <BellRing className="h-4 w-4 mr-1" />
                    Set Up Reminders
                  </Button>
                </div>
              )}
              
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {studyPlan.sessions.map(session => (
                  <div key={session.id} className="p-3 border rounded-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="font-medium">{session.topic}</span>
                        <div className="flex items-center text-sm text-muted-foreground mt-1">
                          <Calendar className="h-3 w-3 mr-1" />
                          <span>{formatDate(session.date)}</span>
                          <Clock className="h-3 w-3 ml-2 mr-1" />
                          <span>{session.duration} hour{session.duration > 1 ? 's' : ''}</span>
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${getSessionTypeStyle(session.type)}`}>
                        {session.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudyPlanner;