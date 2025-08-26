"""
Parallel processor module for AI Note System.
Provides utilities for parallel processing of multiple items.
"""

import logging
import concurrent.futures
from typing import List, Callable, Any, Dict, Optional, Union, TypeVar, Generic

# Create a logger for this module
logger = logging.getLogger("ai_note_system.utils.parallel_processor")

# Define a type variable for the input and output types
T = TypeVar('T')
U = TypeVar('U')

class ParallelProcessor(Generic[T, U]):
    """
    Parallel processor for processing multiple items concurrently.
    
    Generic type parameters:
    - T: Type of input items
    - U: Type of output items
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_threads: bool = True):
        """
        Initialize the parallel processor.
        
        Args:
            max_workers (int, optional): Maximum number of worker processes/threads.
                If None, uses the default (number of processors * 5 for threads, number of processors for processes).
            use_threads (bool): Whether to use threads (True) or processes (False).
                Threads are faster for I/O-bound tasks, processes are better for CPU-bound tasks.
        """
        self.max_workers = max_workers
        self.use_threads = use_threads
        
        # Determine the executor class based on use_threads
        self.executor_class = concurrent.futures.ThreadPoolExecutor if use_threads else concurrent.futures.ProcessPoolExecutor
        
        logger.debug(f"Initialized ParallelProcessor with max_workers={max_workers}, use_threads={use_threads}")
    
    def process(self, items: List[T], process_func: Callable[[T], U], show_progress: bool = True) -> List[U]:
        """
        Process multiple items in parallel.
        
        Args:
            items (List[T]): List of items to process
            process_func (Callable[[T], U]): Function to process each item
            show_progress (bool): Whether to show progress
            
        Returns:
            List[U]: List of processed items
        """
        if not items:
            logger.warning("No items to process")
            return []
        
        num_items = len(items)
        logger.info(f"Processing {num_items} items in parallel")
        
        results = []
        
        # Create a progress tracker if requested
        progress_tracker = None
        if show_progress:
            try:
                from tqdm import tqdm
                progress_tracker = tqdm(total=num_items, desc="Processing items")
            except ImportError:
                logger.warning("tqdm not installed, progress will not be shown")
        
        # Process items in parallel
        with self.executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(process_func, item): item for item in items}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update progress if tracking
                    if progress_tracker:
                        progress_tracker.update(1)
                        
                except Exception as e:
                    logger.error(f"Error processing item {item}: {str(e)}")
                    # Append None or an error indicator to maintain order
                    results.append(None)
                    
                    # Update progress if tracking
                    if progress_tracker:
                        progress_tracker.update(1)
        
        # Close progress tracker if used
        if progress_tracker:
            progress_tracker.close()
        
        logger.info(f"Completed processing {num_items} items")
        return results
    
    def process_with_kwargs(self, items: List[T], process_func: Callable[[T, Dict[str, Any]], U], 
                           kwargs: Dict[str, Any], show_progress: bool = True) -> List[U]:
        """
        Process multiple items in parallel with additional keyword arguments.
        
        Args:
            items (List[T]): List of items to process
            process_func (Callable[[T, Dict[str, Any]], U]): Function to process each item with kwargs
            kwargs (Dict[str, Any]): Keyword arguments to pass to the process function
            show_progress (bool): Whether to show progress
            
        Returns:
            List[U]: List of processed items
        """
        # Create a wrapper function that includes the kwargs
        def wrapper(item: T) -> U:
            return process_func(item, **kwargs)
        
        # Use the regular process method with the wrapper
        return self.process(items, wrapper, show_progress)
    
    def process_with_index(self, items: List[T], process_func: Callable[[T, int], U], 
                          show_progress: bool = True) -> List[U]:
        """
        Process multiple items in parallel, passing the index to the process function.
        
        Args:
            items (List[T]): List of items to process
            process_func (Callable[[T, int], U]): Function to process each item with its index
            show_progress (bool): Whether to show progress
            
        Returns:
            List[U]: List of processed items
        """
        # Create a list of (item, index) tuples
        indexed_items = list(enumerate(items))
        
        # Create a wrapper function that unpacks the tuple
        def wrapper(indexed_item: tuple) -> U:
            index, item = indexed_item
            return process_func(item, index)
        
        # Use the regular process method with the wrapper
        return self.process(indexed_items, wrapper, show_progress)
    
    def process_batch(self, items: List[T], process_func: Callable[[List[T]], List[U]], 
                     batch_size: int = 10, show_progress: bool = True) -> List[U]:
        """
        Process items in batches.
        
        Args:
            items (List[T]): List of items to process
            process_func (Callable[[List[T]], List[U]]): Function to process a batch of items
            batch_size (int): Size of each batch
            show_progress (bool): Whether to show progress
            
        Returns:
            List[U]: List of processed items
        """
        if not items:
            logger.warning("No items to process")
            return []
        
        # Create batches
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        num_batches = len(batches)
        
        logger.info(f"Processing {len(items)} items in {num_batches} batches of size {batch_size}")
        
        # Process batches in parallel
        batch_results = self.process(batches, process_func, show_progress)
        
        # Flatten the results
        results = []
        for batch_result in batch_results:
            if batch_result:
                results.extend(batch_result)
        
        return results

# Example usage for YouTube video processing
def process_youtube_videos_parallel(urls: List[str], max_workers: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Process multiple YouTube videos in parallel.
    
    Args:
        urls (List[str]): List of YouTube video URLs
        max_workers (int, optional): Maximum number of worker threads
        **kwargs: Additional arguments to pass to process_youtube_video
        
    Returns:
        List[Dict[str, Any]]: List of results for each video
    """
    from ..inputs.youtube import process_youtube_video
    
    logger.info(f"Processing {len(urls)} YouTube videos in parallel")
    
    # Create a parallel processor
    processor = ParallelProcessor[str, Dict[str, Any]](max_workers=max_workers, use_threads=True)
    
    # Process videos in parallel
    results = processor.process_with_kwargs(urls, process_youtube_video, kwargs)
    
    return results

# Example usage for PDF processing
def process_pdfs_parallel(pdf_paths: List[str], max_workers: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Process multiple PDF files in parallel.
    
    Args:
        pdf_paths (List[str]): List of paths to PDF files
        max_workers (int, optional): Maximum number of worker threads
        **kwargs: Additional arguments to pass to extract_text_from_pdf
        
    Returns:
        List[Dict[str, Any]]: List of results for each PDF
    """
    from ..inputs.pdf_input import extract_text_from_pdf
    
    logger.info(f"Processing {len(pdf_paths)} PDF files in parallel")
    
    # Create a parallel processor
    processor = ParallelProcessor[str, Dict[str, Any]](max_workers=max_workers, use_threads=True)
    
    # Process PDFs in parallel
    results = processor.process_with_kwargs(pdf_paths, extract_text_from_pdf, kwargs)
    
    return results