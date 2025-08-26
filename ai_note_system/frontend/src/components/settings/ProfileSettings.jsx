import React, { useState } from 'react';
import { 
  User, Moon, Sun, Bell, Globe, Key, ArrowLeft, Upload, Check, X, 
  BellOff, Laptop, Palette, LogOut
} from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for available languages
const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'ru', name: 'Russian' },
];

// Mock data for available themes
const THEMES = [
  { id: 'light', name: 'Light', icon: <Sun className="h-4 w-4" /> },
  { id: 'dark', name: 'Dark', icon: <Moon className="h-4 w-4" /> },
  { id: 'system', name: 'System', icon: <Laptop className="h-4 w-4" /> },
];

// Mock data for LLM providers
const LLM_PROVIDERS = [
  { id: 'openai', name: 'OpenAI' },
  { id: 'anthropic', name: 'Anthropic' },
  { id: 'google', name: 'Google AI' },
  { id: 'local', name: 'Local LLM' },
];

const ProfileSettings = ({ onBack }) => {
  // User profile state
  const [avatar, setAvatar] = useState(null);
  const [username, setUsername] = useState('Aarav');
  const [email, setEmail] = useState('aarav@example.com');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [tempUsername, setTempUsername] = useState(username);
  const [tempEmail, setTempEmail] = useState(email);
  
  // Settings state
  const [activeTab, setActiveTab] = useState('profile');
  const [theme, setTheme] = useState('system');
  const [language, setLanguage] = useState('en');
  const [notifications, setNotifications] = useState({
    email: true,
    browser: true,
    studyReminders: true,
    updates: false,
  });
  
  // API keys state
  const [apiKeys, setApiKeys] = useState({
    openai: '••••••••••••••••••••••••••',
    anthropic: '',
    google: '',
    local: '',
  });
  const [showApiKey, setShowApiKey] = useState(null);
  const [isEditingApiKey, setIsEditingApiKey] = useState(null);
  const [tempApiKey, setTempApiKey] = useState('');
  
  // Handle avatar upload
  const handleAvatarUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatar(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };
  
  // Handle profile edit
  const startEditingProfile = () => {
    setTempUsername(username);
    setTempEmail(email);
    setIsEditingProfile(true);
  };
  
  const saveProfileEdit = () => {
    setUsername(tempUsername);
    setEmail(tempEmail);
    setIsEditingProfile(false);
  };
  
  const cancelProfileEdit = () => {
    setIsEditingProfile(false);
  };
  
  // Handle theme change
  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    // In a real implementation, this would apply the theme to the application
    console.log(`Theme changed to ${newTheme}`);
  };
  
  // Handle language change
  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
    // In a real implementation, this would change the application language
    console.log(`Language changed to ${e.target.value}`);
  };
  
  // Handle notification toggle
  const handleNotificationToggle = (type) => {
    setNotifications({
      ...notifications,
      [type]: !notifications[type],
    });
  };
  
  // Handle API key management
  const toggleShowApiKey = (provider) => {
    setShowApiKey(showApiKey === provider ? null : provider);
  };
  
  const startEditingApiKey = (provider) => {
    setIsEditingApiKey(provider);
    setTempApiKey(apiKeys[provider]);
  };
  
  const saveApiKey = (provider) => {
    setApiKeys({
      ...apiKeys,
      [provider]: tempApiKey,
    });
    setIsEditingApiKey(null);
    setShowApiKey(null);
  };
  
  const cancelEditingApiKey = () => {
    setIsEditingApiKey(null);
  };
  
  // Render profile tab
  const renderProfileTab = () => (
    <div>
      <div className="flex items-center mb-6">
        <div className="relative mr-4">
          <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center overflow-hidden">
            {avatar ? (
              <img src={avatar} alt="User avatar" className="w-full h-full object-cover" />
            ) : (
              <User className="h-10 w-10 text-muted-foreground" />
            )}
          </div>
          <label className="absolute bottom-0 right-0 bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center cursor-pointer">
            <Upload className="h-3 w-3" />
            <input 
              type="file" 
              accept="image/*" 
              className="hidden" 
              onChange={handleAvatarUpload}
              disabled={isEditingProfile}
            />
          </label>
        </div>
        
        <div className="flex-1">
          {isEditingProfile ? (
            <div className="space-y-2">
              <div>
                <label htmlFor="username" className="block text-sm font-medium mb-1">Username</label>
                <input
                  type="text"
                  id="username"
                  value={tempUsername}
                  onChange={(e) => setTempUsername(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
                <input
                  type="email"
                  id="email"
                  value={tempEmail}
                  onChange={(e) => setTempEmail(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={saveProfileEdit}>
                  <Check className="h-4 w-4 mr-1" />
                  Save
                </Button>
                <Button variant="outline" size="sm" onClick={cancelProfileEdit}>
                  <X className="h-4 w-4 mr-1" />
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div>
              <h2 className="text-xl font-bold">{username}</h2>
              <p className="text-muted-foreground">{email}</p>
              <Button variant="outline" size="sm" className="mt-2" onClick={startEditingProfile}>
                Edit Profile
              </Button>
            </div>
          )}
        </div>
      </div>
      
      <div className="border-t pt-4">
        <h3 className="font-medium mb-3">Account</h3>
        <div className="space-y-2">
          <Button variant="outline" className="w-full justify-start" size="sm">
            <Key className="h-4 w-4 mr-2" />
            Change Password
          </Button>
          <Button variant="outline" className="w-full justify-start" size="sm">
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  );
  
  // Render appearance tab
  const renderAppearanceTab = () => (
    <div>
      <h3 className="font-medium mb-3">Theme</h3>
      <div className="grid grid-cols-3 gap-2 mb-6">
        {THEMES.map(themeOption => (
          <button
            key={themeOption.id}
            className={`p-3 rounded-md border flex flex-col items-center justify-center gap-2 ${
              theme === themeOption.id ? 'border-primary bg-primary/10' : 'border-input hover:bg-muted/50'
            }`}
            onClick={() => handleThemeChange(themeOption.id)}
          >
            {themeOption.icon}
            <span className="text-sm">{themeOption.name}</span>
          </button>
        ))}
      </div>
      
      <h3 className="font-medium mb-3">Colors</h3>
      <div className="grid grid-cols-4 gap-2 mb-6">
        <button className="w-full h-10 rounded-md bg-blue-500 hover:opacity-90"></button>
        <button className="w-full h-10 rounded-md bg-green-500 hover:opacity-90"></button>
        <button className="w-full h-10 rounded-md bg-purple-500 hover:opacity-90"></button>
        <button className="w-full h-10 rounded-md bg-orange-500 hover:opacity-90"></button>
      </div>
      
      <h3 className="font-medium mb-3">Font Size</h3>
      <div className="mb-6">
        <input
          type="range"
          min="12"
          max="20"
          step="1"
          defaultValue="16"
          className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>Small</span>
          <span>Medium</span>
          <span>Large</span>
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Palette className="h-4 w-4 mr-2" />
          <span className="text-sm font-medium">Custom CSS</span>
        </div>
        <Button variant="outline" size="sm">
          Edit
        </Button>
      </div>
    </div>
  );
  
  // Render notifications tab
  const renderNotificationsTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Email Notifications</h3>
          <p className="text-sm text-muted-foreground">Receive notifications via email</p>
        </div>
        <button
          className={`w-12 h-6 rounded-full ${notifications.email ? 'bg-primary' : 'bg-muted'} relative`}
          onClick={() => handleNotificationToggle('email')}
        >
          <span 
            className={`absolute top-1 ${notifications.email ? 'right-1' : 'left-1'} w-4 h-4 rounded-full bg-white transition-all`}
          ></span>
        </button>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Browser Notifications</h3>
          <p className="text-sm text-muted-foreground">Show desktop notifications</p>
        </div>
        <button
          className={`w-12 h-6 rounded-full ${notifications.browser ? 'bg-primary' : 'bg-muted'} relative`}
          onClick={() => handleNotificationToggle('browser')}
        >
          <span 
            className={`absolute top-1 ${notifications.browser ? 'right-1' : 'left-1'} w-4 h-4 rounded-full bg-white transition-all`}
          ></span>
        </button>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Study Reminders</h3>
          <p className="text-sm text-muted-foreground">Remind you of scheduled study sessions</p>
        </div>
        <button
          className={`w-12 h-6 rounded-full ${notifications.studyReminders ? 'bg-primary' : 'bg-muted'} relative`}
          onClick={() => handleNotificationToggle('studyReminders')}
        >
          <span 
            className={`absolute top-1 ${notifications.studyReminders ? 'right-1' : 'left-1'} w-4 h-4 rounded-full bg-white transition-all`}
          ></span>
        </button>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Product Updates</h3>
          <p className="text-sm text-muted-foreground">Receive updates about new features</p>
        </div>
        <button
          className={`w-12 h-6 rounded-full ${notifications.updates ? 'bg-primary' : 'bg-muted'} relative`}
          onClick={() => handleNotificationToggle('updates')}
        >
          <span 
            className={`absolute top-1 ${notifications.updates ? 'right-1' : 'left-1'} w-4 h-4 rounded-full bg-white transition-all`}
          ></span>
        </button>
      </div>
      
      <div className="pt-4 border-t">
        <Button variant="outline" size="sm" className="w-full">
          <BellOff className="h-4 w-4 mr-2" />
          Mute All Notifications
        </Button>
      </div>
    </div>
  );
  
  // Render language tab
  const renderLanguageTab = () => (
    <div>
      <h3 className="font-medium mb-3">Application Language</h3>
      <div className="mb-6">
        <select
          value={language}
          onChange={handleLanguageChange}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          {LANGUAGES.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>
      
      <h3 className="font-medium mb-3">Content Translation</h3>
      <div className="space-y-2 mb-6">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="autoTranslate"
            className="mr-2"
          />
          <label htmlFor="autoTranslate" className="text-sm">Automatically translate content</label>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="showOriginal"
            className="mr-2"
          />
          <label htmlFor="showOriginal" className="text-sm">Show original text alongside translation</label>
        </div>
      </div>
      
      <h3 className="font-medium mb-3">Date & Time Format</h3>
      <div className="space-y-2">
        <div>
          <label htmlFor="dateFormat" className="block text-sm mb-1">Date Format</label>
          <select
            id="dateFormat"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
          </select>
        </div>
        <div>
          <label htmlFor="timeFormat" className="block text-sm mb-1">Time Format</label>
          <select
            id="timeFormat"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="12h">12-hour (AM/PM)</option>
            <option value="24h">24-hour</option>
          </select>
        </div>
      </div>
    </div>
  );
  
  // Render API keys tab
  const renderApiKeysTab = () => (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground mb-4">
        Add your API keys to use external language models and services. Your keys are stored securely and never shared.
      </p>
      
      {LLM_PROVIDERS.map(provider => (
        <div key={provider.id} className="border rounded-md p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium">{provider.name}</h3>
            {isEditingApiKey === provider.id ? (
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" onClick={() => saveApiKey(provider.id)}>
                  <Check className="h-4 w-4 text-green-500" />
                </Button>
                <Button variant="ghost" size="sm" onClick={cancelEditingApiKey}>
                  <X className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            ) : (
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" onClick={() => toggleShowApiKey(provider.id)}>
                  {showApiKey === provider.id ? 'Hide' : 'Show'}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => startEditingApiKey(provider.id)}>
                  Edit
                </Button>
              </div>
            )}
          </div>
          
          {isEditingApiKey === provider.id ? (
            <input
              type="text"
              value={tempApiKey}
              onChange={(e) => setTempApiKey(e.target.value)}
              placeholder={`Enter your ${provider.name} API key`}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              autoFocus
            />
          ) : (
            <div className="font-mono text-sm bg-muted p-2 rounded">
              {showApiKey === provider.id ? apiKeys[provider.id] || 'No API key set' : apiKeys[provider.id] ? '••••••••••••••••••••••••••' : 'No API key set'}
            </div>
          )}
        </div>
      ))}
      
      <div className="pt-4">
        <Button variant="outline" size="sm" className="w-full">
          <Key className="h-4 w-4 mr-2" />
          Test API Keys
        </Button>
      </div>
    </div>
  );
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Profile & Settings</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 flex-1">
        <div className="md:col-span-1">
          <nav className="space-y-1">
            <button
              className={`w-full flex items-center px-3 py-2 text-sm rounded-md ${activeTab === 'profile' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
              onClick={() => setActiveTab('profile')}
            >
              <User className="h-4 w-4 mr-2" />
              Profile
            </button>
            <button
              className={`w-full flex items-center px-3 py-2 text-sm rounded-md ${activeTab === 'appearance' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
              onClick={() => setActiveTab('appearance')}
            >
              <Sun className="h-4 w-4 mr-2" />
              Appearance
            </button>
            <button
              className={`w-full flex items-center px-3 py-2 text-sm rounded-md ${activeTab === 'notifications' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
              onClick={() => setActiveTab('notifications')}
            >
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </button>
            <button
              className={`w-full flex items-center px-3 py-2 text-sm rounded-md ${activeTab === 'language' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
              onClick={() => setActiveTab('language')}
            >
              <Globe className="h-4 w-4 mr-2" />
              Language
            </button>
            <button
              className={`w-full flex items-center px-3 py-2 text-sm rounded-md ${activeTab === 'apikeys' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
              onClick={() => setActiveTab('apikeys')}
            >
              <Key className="h-4 w-4 mr-2" />
              API Keys
            </button>
          </nav>
        </div>
        
        <div className="md:col-span-3 border rounded-md p-6">
          {activeTab === 'profile' && renderProfileTab()}
          {activeTab === 'appearance' && renderAppearanceTab()}
          {activeTab === 'notifications' && renderNotificationsTab()}
          {activeTab === 'language' && renderLanguageTab()}
          {activeTab === 'apikeys' && renderApiKeysTab()}
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;