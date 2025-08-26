import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Image, 
  Mic, 
  Youtube, 
  Upload, 
  Link as LinkIcon, 
  FileUp, 
  Clipboard, 
  Loader2,
  ChevronRight,
  Check,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

// Input type options
const inputTypes = [
  { id: 'text', label: 'Text', icon: FileText, description: 'Process raw text or paste content' },
  { id: 'pdf', label: 'PDF', icon: FileUp, description: 'Upload and process PDF documents' },
  { id: 'image', label: 'Image', icon: Image, description: 'Extract text from images using OCR' },
  { id: 'voice', label: 'Voice', icon: Mic, description: 'Record and transcribe voice notes' },
  { id: 'youtube', label: 'YouTube', icon: Youtube, description: 'Process YouTube video transcripts' },
  { id: 'url', label: 'URL', icon: LinkIcon, description: 'Extract content from web pages' },
];

// Processing options
const processingOptions = [
  { id: 'summarize', label: 'Generate Summary', description: 'Create a concise summary of the content' },
  { id: 'keypoints', label: 'Extract Key Points', description: 'Identify and extract the main points' },
  { id: 'questions', label: 'Generate Questions', description: 'Create questions for active recall' },
  { id: 'glossary', label: 'Create Glossary', description: 'Extract important terms and definitions' },
  { id: 'visualize', label: 'Generate Visualizations', description: 'Create visual representations of the content' },
];

export default function ProcessInput() {
  const { toast } = useToast();
  const [selectedType, setSelectedType] = useState('text');
  const [inputContent, setInputContent] = useState('');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedOptions, setSelectedOptions] = useState(['summarize', 'keypoints']);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [processingComplete, setProcessingComplete] = useState(false);

  // Toggle processing option selection
  const toggleOption = (optionId) => {
    if (selectedOptions.includes(optionId)) {
      setSelectedOptions(selectedOptions.filter(id => id !== optionId));
    } else {
      setSelectedOptions([...selectedOptions, optionId]);
    }
  };

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      toast({
        title: 'File Selected',
        description: `${file.name} (${(file.size / 1024).toFixed(2)} KB)`,
      });
    }
  };

  // Handle recording toggle
  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      toast({
        title: 'Recording Stopped',
        description: 'Voice recording has been stopped and is ready for processing',
      });
    } else {
      setIsRecording(true);
      toast({
        title: 'Recording Started',
        description: 'Speak clearly into your microphone',
      });
    }
  };

  // Process the input
  const processInput = () => {
    // Validate input based on selected type
    if (selectedType === 'text' && !inputContent.trim()) {
      toast({
        title: 'Empty Input',
        description: 'Please enter some text to process',
        variant: 'destructive',
      });
      return;
    }

    if (selectedType === 'pdf' && !selectedFile) {
      toast({
        title: 'No File Selected',
        description: 'Please select a PDF file to process',
        variant: 'destructive',
      });
      return;
    }

    if (selectedType === 'image' && !selectedFile) {
      toast({
        title: 'No Image Selected',
        description: 'Please select an image to process',
        variant: 'destructive',
      });
      return;
    }

    if (selectedType === 'youtube' && !youtubeUrl.trim()) {
      toast({
        title: 'No YouTube URL',
        description: 'Please enter a YouTube video URL',
        variant: 'destructive',
      });
      return;
    }

    if (selectedType === 'url' && !webUrl.trim()) {
      toast({
        title: 'No Web URL',
        description: 'Please enter a web page URL',
        variant: 'destructive',
      });
      return;
    }

    if (selectedOptions.length === 0) {
      toast({
        title: 'No Processing Options',
        description: 'Please select at least one processing option',
        variant: 'destructive',
      });
      return;
    }

    // Start processing
    setIsProcessing(true);
    setProcessingStep(1);

    // Simulate processing steps
    const totalSteps = selectedOptions.length + 2; // Input processing + options + finalization
    
    const processSteps = async () => {
      // Step 1: Process input
      await new Promise(resolve => setTimeout(resolve, 1500));
      setProcessingStep(2);
      
      // Steps 2 to n-1: Process selected options
      for (let i = 0; i < selectedOptions.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setProcessingStep(3 + i);
      }
      
      // Final step: Complete processing
      await new Promise(resolve => setTimeout(resolve, 1000));
      setProcessingComplete(true);
      setIsProcessing(false);
      
      toast({
        title: 'Processing Complete',
        description: 'Your input has been processed successfully',
      });
    };
    
    processSteps();
  };

  // Reset the form
  const resetForm = () => {
    setInputContent('');
    setYoutubeUrl('');
    setWebUrl('');
    setSelectedFile(null);
    setSelectedOptions(['summarize', 'keypoints']);
    setIsProcessing(false);
    setProcessingStep(0);
    setProcessingComplete(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Process Input</h1>
        {processingComplete && (
          <Button onClick={resetForm} variant="outline">
            Process New Input
          </Button>
        )}
      </div>

      {!isProcessing && !processingComplete ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Input Type Selection */}
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Select Input Type</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {inputTypes.map((type) => (
                <div
                  key={type.id}
                  className={`flex items-start p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedType === type.id
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50 hover:bg-secondary'
                  }`}
                  onClick={() => setSelectedType(type.id)}
                >
                  <div className={`p-2 rounded-full ${
                    selectedType === type.id ? 'bg-primary/20' : 'bg-secondary'
                  }`}>
                    <type.icon className={`h-5 w-5 ${
                      selectedType === type.id ? 'text-primary' : 'text-muted-foreground'
                    }`} />
                  </div>
                  <div className="ml-4">
                    <h3 className="font-medium">{type.label}</h3>
                    <p className="text-sm text-muted-foreground">{type.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Input Content */}
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Input Content</h2>
            
            {selectedType === 'text' && (
              <div className="space-y-2">
                <textarea
                  value={inputContent}
                  onChange={(e) => setInputContent(e.target.value)}
                  placeholder="Enter or paste your text here..."
                  className="w-full h-40 p-4 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                />
                <div className="flex justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.readText().then(text => {
                        setInputContent(text);
                        toast({
                          title: 'Text Pasted',
                          description: 'Content has been pasted from clipboard',
                        });
                      }).catch(err => {
                        toast({
                          title: 'Paste Failed',
                          description: 'Could not access clipboard content',
                          variant: 'destructive',
                        });
                      });
                    }}
                  >
                    <Clipboard className="mr-2 h-4 w-4" />
                    Paste from Clipboard
                  </Button>
                </div>
              </div>
            )}
            
            {selectedType === 'pdf' && (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-4" />
                  <h3 className="font-medium mb-2">Upload PDF Document</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Drag and drop your PDF file here, or click to browse
                  </p>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="pdf-upload"
                  />
                  <Button asChild>
                    <label htmlFor="pdf-upload">
                      <FileUp className="mr-2 h-4 w-4" />
                      Browse Files
                    </label>
                  </Button>
                </div>
                {selectedFile && (
                  <div className="bg-secondary p-3 rounded-md flex items-center justify-between">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-primary mr-2" />
                      <span className="font-medium">{selectedFile.name}</span>
                      <span className="text-sm text-muted-foreground ml-2">
                        ({(selectedFile.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedFile(null)}
                    >
                      Remove
                    </Button>
                  </div>
                )}
              </div>
            )}
            
            {selectedType === 'image' && (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <Image className="h-10 w-10 text-muted-foreground mx-auto mb-4" />
                  <h3 className="font-medium mb-2">Upload Image</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Drag and drop your image here, or click to browse
                  </p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                    id="image-upload"
                  />
                  <Button asChild>
                    <label htmlFor="image-upload">
                      <FileUp className="mr-2 h-4 w-4" />
                      Browse Files
                    </label>
                  </Button>
                </div>
                {selectedFile && (
                  <div className="bg-secondary p-3 rounded-md flex items-center justify-between">
                    <div className="flex items-center">
                      <Image className="h-5 w-5 text-primary mr-2" />
                      <span className="font-medium">{selectedFile.name}</span>
                      <span className="text-sm text-muted-foreground ml-2">
                        ({(selectedFile.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedFile(null)}
                    >
                      Remove
                    </Button>
                  </div>
                )}
              </div>
            )}
            
            {selectedType === 'voice' && (
              <div className="space-y-4 text-center">
                <div className={`border-2 rounded-lg p-8 ${isRecording ? 'border-destructive bg-destructive/10 animate-pulse' : 'border-border'}`}>
                  <Mic className={`h-10 w-10 mx-auto mb-4 ${isRecording ? 'text-destructive' : 'text-muted-foreground'}`} />
                  <h3 className="font-medium mb-2">
                    {isRecording ? 'Recording in Progress...' : 'Record Voice Note'}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {isRecording 
                      ? 'Speak clearly into your microphone. Click stop when finished.' 
                      : 'Click the button below to start recording your voice note.'}
                  </p>
                  <Button 
                    variant={isRecording ? "destructive" : "default"}
                    onClick={toggleRecording}
                  >
                    {isRecording ? (
                      <>Stop Recording</>
                    ) : (
                      <>Start Recording</>
                    )}
                  </Button>
                </div>
                {isRecording && (
                  <div className="text-sm text-muted-foreground">
                    Recording duration: 00:00:15
                  </div>
                )}
              </div>
            )}
            
            {selectedType === 'youtube' && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Youtube className="h-5 w-5 text-muted-foreground" />
                  <input
                    type="text"
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    placeholder="Enter YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)"
                    className="flex-1 p-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div className="text-sm text-muted-foreground">
                  <p>The system will extract the transcript from the YouTube video and process it according to your selected options.</p>
                </div>
              </div>
            )}
            
            {selectedType === 'url' && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <LinkIcon className="h-5 w-5 text-muted-foreground" />
                  <input
                    type="text"
                    value={webUrl}
                    onChange={(e) => setWebUrl(e.target.value)}
                    placeholder="Enter web page URL (e.g., https://example.com/article)"
                    className="flex-1 p-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div className="text-sm text-muted-foreground">
                  <p>The system will extract the main content from the web page and process it according to your selected options.</p>
                </div>
              </div>
            )}
          </div>

          {/* Processing Options */}
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Processing Options</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {processingOptions.map((option) => (
                <div
                  key={option.id}
                  className={`flex items-start p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedOptions.includes(option.id)
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50 hover:bg-secondary'
                  }`}
                  onClick={() => toggleOption(option.id)}
                >
                  <div className={`p-2 rounded-full ${
                    selectedOptions.includes(option.id) ? 'bg-primary/20' : 'bg-secondary'
                  }`}>
                    <Check className={`h-5 w-5 ${
                      selectedOptions.includes(option.id) ? 'text-primary' : 'text-muted-foreground/30'
                    }`} />
                  </div>
                  <div className="ml-4">
                    <h3 className="font-medium">{option.label}</h3>
                    <p className="text-sm text-muted-foreground">{option.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Process Button */}
          <div className="flex justify-end">
            <Button onClick={processInput} size="lg">
              Process Input
              <ChevronRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-card rounded-lg border border-border p-8"
        >
          {processingComplete ? (
            <div className="text-center space-y-6">
              <div className="bg-primary/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto">
                <Check className="h-10 w-10 text-primary" />
              </div>
              <h2 className="text-2xl font-bold">Processing Complete</h2>
              <p className="text-muted-foreground max-w-md mx-auto">
                Your input has been processed successfully. You can now view the results or process another input.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                <Button>
                  View Results
                </Button>
                <Button variant="outline" onClick={resetForm}>
                  Process New Input
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              <div className="flex justify-center">
                <div className="w-full max-w-md">
                  <div className="relative">
                    <div className="overflow-hidden h-2 text-xs flex rounded bg-secondary">
                      <motion.div
                        initial={{ width: '0%' }}
                        animate={{ width: `${(processingStep / (selectedOptions.length + 2)) * 100}%` }}
                        className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary"
                      ></motion.div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="text-center space-y-4">
                <div className="bg-primary/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto">
                  <Loader2 className="h-10 w-10 text-primary animate-spin" />
                </div>
                <h2 className="text-2xl font-bold">Processing Your Input</h2>
                <p className="text-muted-foreground">
                  {processingStep === 1 && `Analyzing ${selectedType} input...`}
                  {processingStep === 2 && 'Extracting content...'}
                  {processingStep > 2 && processingStep <= 2 + selectedOptions.length && 
                    `Generating ${processingOptions.find(o => o.id === selectedOptions[processingStep - 3])?.label}...`}
                </p>
              </div>
              
              <div className="space-y-4 max-w-md mx-auto">
                <div className={`flex items-center gap-3 p-3 rounded-md ${processingStep > 0 ? 'bg-primary/10' : 'bg-secondary'}`}>
                  <div className={`p-1 rounded-full ${processingStep > 0 ? 'bg-primary/20' : 'bg-muted'}`}>
                    {processingStep > 0 ? (
                      <Check className="h-4 w-4 text-primary" />
                    ) : (
                      <div className="h-4 w-4" />
                    )}
                  </div>
                  <span>Analyzing input</span>
                </div>
                
                <div className={`flex items-center gap-3 p-3 rounded-md ${processingStep > 1 ? 'bg-primary/10' : 'bg-secondary'}`}>
                  <div className={`p-1 rounded-full ${processingStep > 1 ? 'bg-primary/20' : 'bg-muted'}`}>
                    {processingStep > 1 ? (
                      <Check className="h-4 w-4 text-primary" />
                    ) : (
                      <div className="h-4 w-4" />
                    )}
                  </div>
                  <span>Extracting content</span>
                </div>
                
                {selectedOptions.map((option, index) => (
                  <div 
                    key={option}
                    className={`flex items-center gap-3 p-3 rounded-md ${processingStep > index + 2 ? 'bg-primary/10' : 'bg-secondary'}`}
                  >
                    <div className={`p-1 rounded-full ${processingStep > index + 2 ? 'bg-primary/20' : 'bg-muted'}`}>
                      {processingStep > index + 2 ? (
                        <Check className="h-4 w-4 text-primary" />
                      ) : (
                        <div className="h-4 w-4" />
                      )}
                    </div>
                    <span>Generating {processingOptions.find(o => o.id === option)?.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}