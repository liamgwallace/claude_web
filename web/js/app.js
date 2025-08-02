class ClaudeWebApp {
    constructor() {
        // Check if CSS loaded properly and apply fallback if needed
        this.checkCSSLoading();
        
        // Detect if we're behind a proxy and set API base accordingly
        const currentPath = window.location.pathname;
        if (currentPath.includes('/proxy/')) {
            // Extract the proxy path (e.g., '/proxy/8000')
            const proxyMatch = currentPath.match(/\/proxy\/\d+/);
            this.apiBase = proxyMatch ? proxyMatch[0] : '';
        } else {
            this.apiBase = ''; // Use relative URLs for normal setup
        }
        this.currentProject = null;
        this.currentThread = null;
        this.isLoading = false;
        this.initialHashLoad = true;
        
        // Mobile keyboard handling
        this.initialViewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
        this.keyboardOpen = false;
        this.scrollPosition = 0;
        
        this.initializeElements();
        this.bindEvents();
        
        // Ensure mobile layout classes are applied properly
        if (window.innerWidth <= 768) {
            this.ensureMobileLayout();
        }
        
        this.initializeSidebarStates();
        this.initializeRouting();
        this.loadInitialData();
        this.initializeMobileHandling();
        
        // Ensure mobile layout is properly set up
        if (window.innerWidth <= 768) {
            setTimeout(() => {
                this.ensureMobileLayout();
                this.adjustMobileInputPosition();
            }, 100);
        }
    }

    checkCSSLoading() {
        // Check if main CSS loaded by testing a known class
        setTimeout(() => {
            const testElement = document.querySelector('.header');
            if (testElement) {
                const computedStyle = window.getComputedStyle(testElement);
                const backgroundColor = computedStyle.backgroundColor;
                
                // If header doesn't have the expected dark background, CSS didn't load
                if (!backgroundColor || backgroundColor === 'rgba(0, 0, 0, 0)' || backgroundColor === 'transparent') {
                    console.warn('CSS failed to load, applying fallback styles');
                    this.applyFallbackCSS();
                }
            }
        }, 500);
    }


    applyFallbackCSS() {
        const style = document.createElement('style');
        style.textContent = `
            /* Emergency fallback CSS for mobile */
            .header { background: #2c3e50 !important; color: white !important; }
            .sidebar-toggle { background: none !important; border: none !important; color: white !important; padding: 8px !important; }
            .header-title { font-weight: 600 !important; }
            .left-sidebar { background: white !important; border-right: 1px solid #e1e5e9 !important; }
            .right-sidebar { background: white !important; border-left: 1px solid #e1e5e9 !important; }
            .chat-area { background: white !important; }
            .message-bubble { padding: 12px 16px !important; border-radius: 18px !important; }
            .message.user .message-bubble { background: #007bff !important; color: white !important; }
            .message.assistant .message-bubble { background: #f1f3f4 !important; color: white !important; }
            .input-field { border: 1px solid #d1d5db !important; border-radius: 22px !important; padding: 12px 16px !important; }
            .send-btn { background: #007bff !important; color: white !important; border-radius: 50% !important; }
            .sidebar-btn { border: 1px solid #dee2e6 !important; background: white !important; padding: 8px 12px !important; }
            .sidebar-btn.primary { background: #007bff !important; color: white !important; }
            .sidebar-btn.danger { background: #dc3545 !important; color: white !important; }
        `;
        document.head.appendChild(style);
    }

    initializeElements() {
        // Sidebar toggles
        this.leftSidebarToggle = document.getElementById('leftSidebarToggle');
        this.rightSidebarToggle = document.getElementById('rightSidebarToggle');
        this.leftSidebar = document.getElementById('leftSidebar');
        this.rightSidebar = document.getElementById('rightSidebar');
        this.chatArea = document.getElementById('chatArea');
        this.overlay = document.getElementById('overlay');

        // Content areas
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');

        // Trees and info
        this.projectTree = document.getElementById('projectTree');
        this.fileTree = document.getElementById('fileTree');
        this.currentProjectInfo = document.getElementById('currentProjectInfo');
        this.currentProjectFiles = document.getElementById('currentProjectFiles');

        // Buttons
        this.newProjectBtn = document.getElementById('newProjectBtn');
        this.deleteProjectBtn = document.getElementById('deleteProjectBtn');
        this.newThreadBtn = document.getElementById('newThreadBtn');
        this.deleteThreadBtn = document.getElementById('deleteThreadBtn');
    }

    initializeSidebarStates() {
        // Set initial sidebar states based on screen size
        if (window.innerWidth <= 768) {
            // Mobile: both sidebars closed by default (force state)
            this.leftSidebar.classList.add('closed');
            this.rightSidebar.classList.remove('open');
            // Ensure overlay is hidden
            this.overlay.classList.remove('show');
            document.body.classList.remove('overlay-active');
            console.log('Mobile layout initialized - sidebars closed');
        } else {
            // Desktop: left sidebar open by default
            this.leftSidebar.classList.remove('closed');
            this.rightSidebar.classList.remove('open');
            console.log('Desktop layout initialized');
        }
        
        // Handle window resize with debouncing
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResponsiveLayout();
            }, 150);
        });
    }
    
    ensureMobileLayout() {
        // Simple mobile layout helper - no inline styles
        if (window.innerWidth <= 768) {
            // Ensure mobile classes are applied properly
            this.leftSidebar.classList.add('closed');
            this.rightSidebar.classList.remove('open');
            this.overlay.classList.remove('show');
            document.body.classList.remove('overlay-active');
            console.log('Mobile layout state ensured via CSS classes');
        }
    }
    
    handleResponsiveLayout() {
        if (window.innerWidth <= 768) {
            // Switching to mobile - ensure coordinated behavior
            this.ensureMobileLayout();
            // Ensure input area positioning is correct for mobile
            this.adjustMobileInputPosition();
        } else {
            // Switching to desktop - always close overlay and reset mobile adjustments
            this.overlay.classList.remove('show');
            document.body.classList.remove('overlay-active');
            this.resetDesktopLayout();
        }
    }
    
    adjustMobileInputPosition() {
        // Ensure input area doesn't overlap with content on mobile
        if (window.innerWidth <= 768) {
            const inputArea = document.querySelector('.input-area');
            const chatMessages = document.querySelector('.chat-messages');
            if (inputArea && chatMessages) {
                // Ensure proper spacing for mobile input
                const inputHeight = inputArea.offsetHeight;
                chatMessages.style.paddingBottom = Math.max(inputHeight + 20, 100) + 'px';
            }
        }
    }
    
    resetDesktopLayout() {
        // Reset any mobile-specific adjustments for desktop
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages && window.innerWidth > 768) {
            chatMessages.style.paddingBottom = '0px';
        }
    }

    bindEvents() {
        // Sidebar toggles - add both click and touchend for better mobile support
        this.leftSidebarToggle.addEventListener('click', () => this.toggleLeftSidebar());
        this.leftSidebarToggle.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.toggleLeftSidebar();
        });
        
        this.rightSidebarToggle.addEventListener('click', () => this.toggleRightSidebar());
        this.rightSidebarToggle.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.toggleRightSidebar();
        });
        
        this.overlay.addEventListener('click', () => this.closeSidebars());
        this.overlay.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.closeSidebars();
        });

        // Input events
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.messageInput.addEventListener('focus', () => this.handleInputFocus());
        this.messageInput.addEventListener('blur', () => this.handleInputBlur());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.sendBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Button events - add touch support for mobile
        this.newProjectBtn.addEventListener('click', () => this.createProject());
        this.newProjectBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.createProject();
        });
        
        this.deleteProjectBtn.addEventListener('click', () => this.deleteProject());
        this.deleteProjectBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.deleteProject();
        });
        
        this.newThreadBtn.addEventListener('click', () => this.createThread());
        this.newThreadBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.createThread();
        });
        
        this.deleteThreadBtn.addEventListener('click', () => this.deleteThread());
        this.deleteThreadBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.deleteThread();
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Hash change listener for browser navigation
        window.addEventListener('hashchange', () => this.handleHashChange());
    }

    initializeRouting() {
        // Handle initial hash on page load
        if (window.location.hash) {
            // Don't auto-navigate on first load - let loadLastSession handle it
            // unless there's a specific hash route
            const hashRoute = this.parseHashRoute(window.location.hash);
            if (hashRoute) {
                this.initialHashLoad = true;
            }
        }
    }

    parseHashRoute(hash) {
        // Parse hash format: #/project/PROJECTNAME/thread/THREADID
        const match = hash.match(/^#\/project\/([^\/]+)\/thread\/([^\/]+)$/);
        if (match) {
            return {
                project: decodeURIComponent(match[1]),
                thread: decodeURIComponent(match[2])
            };
        }
        return null;
    }

    updateUrl(project, thread) {
        if (project && thread) {
            const newHash = `#/project/${encodeURIComponent(project)}/thread/${encodeURIComponent(thread)}`;
            if (window.location.hash !== newHash) {
                history.replaceState(null, '', newHash);
            }
        }
    }

    async handleHashChange() {
        const route = this.parseHashRoute(window.location.hash);
        if (route) {
            // Navigate to the specified project and thread
            if (route.project !== this.currentProject) {
                await this.selectProject(route.project);
            }
            if (route.thread !== this.currentThread) {
                await this.selectThread(route.thread);
            }
            
            // Update visual selection in sidebar
            this.updateSidebarSelection(route.project, route.thread);
        }
    }

    updateSidebarSelection(projectName, threadId) {
        // Remove all previous selections
        document.querySelectorAll('.tree-item-content.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Find and select the correct thread link
        const threadSelector = `a[data-type="thread"][data-id="${projectName}:${threadId}"]`;
        const threadLinks = document.querySelectorAll(threadSelector);
        threadLinks.forEach(link => {
            link.classList.add('selected');
        });
        
        // Also ensure the project is expanded if the thread is found
        if (threadLinks.length > 0) {
            const projectItem = threadLinks[0].closest('.tree-item').parentElement.closest('.tree-item');
            if (projectItem) {
                const projectIcon = projectItem.querySelector('.tree-icon');
                const projectChildren = projectItem.querySelector('.tree-children');
                if (projectIcon && projectChildren) {
                    projectChildren.style.display = 'block';
                    projectIcon.textContent = '▼';
                }
            }
        }
    }

    async loadInitialData() {
        try {
            await this.loadProjects();
            
            // Check if there's a hash route to load
            const hashRoute = this.parseHashRoute(window.location.hash);
            if (hashRoute && this.initialHashLoad) {
                this.initialHashLoad = false;
                await this.handleHashChange();
            } else {
                await this.loadLastSession();
            }
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.addMessage('assistant', 'Failed to connect to the backend API. Please make sure the server is running.');
        }
    }

    async loadProjects() {
        try {
            const response = await fetch(`${this.apiBase}/projects`);
            const data = await response.json();
            
            if (data.success) {
                this.renderProjectTree(data.projects);
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }

    async loadLastSession() {
        // Try to load the last used project and thread from localStorage
        const lastProject = localStorage.getItem('lastProject');
        const lastThread = localStorage.getItem('lastThread');
        
        if (lastProject) {
            await this.selectProject(lastProject);
            if (lastThread) {
                await this.selectThread(lastThread);
            }
        }
    }

    renderProjectTree(projects) {
        this.projectTree.innerHTML = '';
        
        projects.forEach(project => {
            const projectItem = this.createTreeItem(
                `📁 ${project.name}`,
                'project',
                project.sanitized_name,
                project.thread_count > 0
            );
            
            if (project.thread_count > 0) {
                const threadsList = document.createElement('ul');
                threadsList.className = 'tree-children';
                threadsList.style.display = 'none';
                
                // We'll load threads when project is expanded
                projectItem.appendChild(threadsList);
            }
            
            this.projectTree.appendChild(projectItem);
        });
    }

    createTreeItem(label, type, id, hasChildren = false) {
        const li = document.createElement('li');
        li.className = 'tree-item';
        
        const content = document.createElement('div');
        content.className = 'tree-item-content';
        content.dataset.type = type;
        content.dataset.id = id;
        
        if (hasChildren) {
            const icon = document.createElement('span');
            icon.className = 'tree-icon';
            icon.textContent = '▶';
            content.appendChild(icon);
            
            content.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                this.toggleTreeItem(li, type, id);
            });
            content.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                // Prevent unwanted input focus
                if (document.activeElement && document.activeElement.blur) {
                    document.activeElement.blur();
                }
                this.toggleTreeItem(li, type, id);
            });
        } else {
            content.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                this.selectTreeItem(type, id);
            });
            content.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                // Prevent unwanted input focus
                if (document.activeElement && document.activeElement.blur) {
                    document.activeElement.blur();
                }
                this.selectTreeItem(type, id);
            });
        }
        
        const labelSpan = document.createElement('span');
        labelSpan.className = 'tree-label';
        labelSpan.textContent = label;
        content.appendChild(labelSpan);
        
        li.appendChild(content);
        return li;
    }

    createThreadItem(label, projectName, threadId) {
        const li = document.createElement('li');
        li.className = 'tree-item';
        
        // Create anchor tag with proper URL
        const link = document.createElement('a');
        link.className = 'tree-item-content';
        link.dataset.type = 'thread';
        link.dataset.id = `${projectName}:${threadId}`;
        link.href = `#/project/${encodeURIComponent(projectName)}/thread/${encodeURIComponent(threadId)}`;
        link.style.cssText = 'text-decoration: none; color: inherit; display: flex; align-items: center;';
        
        // Add click handler that prevents default and uses our routing
        link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.navigateToThread(projectName, threadId);
        });
        
        // Add touch handler to prevent unwanted input focus
        link.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            // Prevent unwanted input focus
            if (document.activeElement && document.activeElement.blur) {
                document.activeElement.blur();
            }
            this.navigateToThread(projectName, threadId);
        });
        
        const labelSpan = document.createElement('span');
        labelSpan.className = 'tree-label';
        labelSpan.textContent = label;
        link.appendChild(labelSpan);
        
        li.appendChild(link);
        return li;
    }

    async navigateToThread(projectName, threadId) {
        // Update URL first
        this.updateUrl(projectName, threadId);
        
        // Navigate to project and thread
        if (projectName !== this.currentProject) {
            await this.selectProject(projectName);
        }
        if (threadId !== this.currentThread) {
            await this.selectThread(threadId);
        }
        
        // Update visual selection
        this.updateSidebarSelection(projectName, threadId);
    }

    async toggleTreeItem(li, type, id) {
        const icon = li.querySelector('.tree-icon');
        const children = li.querySelector('.tree-children');
        
        if (type === 'project') {
            if (children.style.display === 'none') {
                // Load and show threads
                await this.loadProjectThreads(id, children);
                children.style.display = 'block';
                icon.textContent = '▼';
            } else {
                // Hide threads
                children.style.display = 'none';
                icon.textContent = '▶';
            }
        }
    }

    async loadProjectThreads(projectName, container) {
        try {
            const response = await fetch(`${this.apiBase}/project/${projectName}/threads`);
            const data = await response.json();
            
            if (data.success) {
                container.innerHTML = '';
                data.threads.forEach(thread => {
                    const threadItem = this.createThreadItem(
                        `💬 ${thread.name} (${thread.message_count})`,
                        projectName,
                        thread.id
                    );
                    container.appendChild(threadItem);
                });
            }
        } catch (error) {
            console.error('Failed to load threads:', error);
        }
    }

    async selectTreeItem(type, id) {
        // Remove previous selections
        document.querySelectorAll('.tree-item-content.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Add selection to current item (if event target exists)
        if (event && event.target) {
            event.target.closest('.tree-item-content').classList.add('selected');
        }
        
        if (type === 'project') {
            await this.selectProject(id);
        } else if (type === 'thread') {
            const [projectName, threadId] = id.split(':');
            await this.navigateToThread(projectName, threadId);
        }
    }

    async selectProject(projectName) {
        this.currentProject = projectName;
        localStorage.setItem('lastProject', projectName);
        
        this.currentProjectInfo.textContent = `Project: ${projectName}`;
        this.currentProjectFiles.textContent = `Files in: ${projectName}`;
        
        // Enable/disable buttons
        this.deleteProjectBtn.disabled = false;
        this.newThreadBtn.disabled = false;
        
        // Load project files
        await this.loadProjectFiles(projectName);
        
        // Clear chat if no thread selected
        if (!this.currentThread) {
            this.clearChat();
            this.addMessage('assistant', `Project "${projectName}" selected. Create or select a thread to start chatting.`);
        }
    }

    async selectThread(threadId) {
        this.currentThread = threadId;
        localStorage.setItem('lastThread', threadId);
        
        // Update URL if we have both project and thread
        if (this.currentProject && threadId) {
            this.updateUrl(this.currentProject, threadId);
        }
        
        // Enable/disable buttons
        this.deleteThreadBtn.disabled = false;
        this.sendBtn.disabled = false;
        this.messageInput.disabled = false;
        
        // Load thread messages (if any)
        this.clearChat();
        await this.loadThreadMessages(threadId);
    }

    async loadProjectFiles(projectName) {
        try {
            const response = await fetch(`${this.apiBase}/project/${projectName}/files`);
            const data = await response.json();
            
            if (data.success && data.file_tree) {
                this.renderFileTree(data.file_tree);
            } else {
                this.fileTree.innerHTML = '<li class="tree-item"><div class="tree-item-content">No files found</div></li>';
            }
        } catch (error) {
            console.error('Failed to load project files:', error);
            this.fileTree.innerHTML = '<li class="tree-item"><div class="tree-item-content">Error loading files</div></li>';
        }
    }

    renderFileTree(node, container = this.fileTree, parentPath = '', isRoot = true) {
        if (container === this.fileTree) {
            container.innerHTML = '';
        }
        
        // Skip the root project directory name in the path
        const currentPath = isRoot ? '' : (parentPath ? `${parentPath}/${node.name}` : node.name);
        const icon = node.type === 'directory' ? '📁' : '📄';
        const item = this.createFileTreeItem(`${icon} ${node.name}`, node.type, currentPath, node.children && node.children.length > 0);
        
        if (node.children && node.children.length > 0) {
            const childContainer = document.createElement('ul');
            childContainer.className = 'tree-children';
            node.children.forEach(child => {
                this.renderFileTree(child, childContainer, currentPath, false);
            });
            item.appendChild(childContainer);
        }
        
        container.appendChild(item);
    }

    toggleLeftSidebar() {
        const isClosed = this.leftSidebar.classList.contains('closed');
        
        if (isClosed) {
            // Opening sidebar - ensure coordinated behavior
            this.leftSidebar.classList.remove('closed');
            if (window.innerWidth <= 768) {
                // Mobile: show overlay and ensure proper coordination
                this.overlay.classList.add('show');
                document.body.classList.add('overlay-active');
                // Ensure input area remains accessible
                this.adjustMobileInputPosition();
            }
            // Desktop: Grid layout handles positioning automatically
        } else {
            // Closing sidebar
            this.leftSidebar.classList.add('closed');
            if (window.innerWidth <= 768) {
                this.overlay.classList.remove('show');
                document.body.classList.remove('overlay-active');
            }
        }
    }

    toggleRightSidebar() {
        const isOpen = this.rightSidebar.classList.contains('open');
        
        if (!isOpen) {
            // Opening sidebar - ensure coordinated behavior
            this.rightSidebar.classList.add('open');
            if (window.innerWidth <= 768) {
                // Mobile: show overlay and ensure proper coordination
                this.overlay.classList.add('show');
                document.body.classList.add('overlay-active');
                // Ensure input area remains accessible
                this.adjustMobileInputPosition();
            }
            // Desktop: Grid layout handles positioning automatically
        } else {
            // Closing sidebar
            this.rightSidebar.classList.remove('open');
            if (window.innerWidth <= 768) {
                this.overlay.classList.remove('show');
                document.body.classList.remove('overlay-active');
            }
        }
    }

    closeSidebars() {
        this.leftSidebar.classList.add('closed');
        this.rightSidebar.classList.remove('open');
        this.overlay.classList.remove('show');
        document.body.classList.remove('overlay-active');
    }

    handleInputChange() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText || this.isLoading || !this.currentThread;
    }

    handleKeyDown(e) {
        if (e.key === 'Enter') {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                if (!this.sendBtn.disabled) {
                    this.sendMessage();
                }
            }
        }
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        const maxHeight = window.innerWidth <= 768 ? 88 : 120;
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, maxHeight) + 'px';
        
        // Adjust mobile input positioning when textarea size changes
        if (window.innerWidth <= 768) {
            setTimeout(() => this.adjustMobileInputPosition(), 50);
        }
    }

    async sendMessage() {
        if (!this.currentProject || !this.currentThread || this.isLoading) {
            return;
        }

        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.handleInputChange();

        // Show loading status
        this.showStatus('Claude is thinking...');
        this.isLoading = true;

        try {
            // Send message to API
            const response = await fetch(`${this.apiBase}/project/${this.currentProject}/thread/${this.currentThread}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            if (data.success) {
                // Poll for response
                await this.pollForResponse(data.job_id);
            } else {
                this.hideStatus();
                this.addMessage('assistant', `Error: ${data.error || 'Failed to send message'}`);
            }
        } catch (error) {
            this.hideStatus();
            this.addMessage('assistant', `Error: ${error.message}`);
        } finally {
            this.isLoading = false;
            this.handleInputChange();
        }
    }

    async pollForResponse(jobId) {
        const maxAttempts = 150; // 5 minutes
        let attempts = 0;

        const poll = async () => {
            try {
                const response = await fetch(`${this.apiBase}/status/${jobId}`);
                const data = await response.json();

                if (data.success) {
                    if (data.status === 'done') {
                        this.hideStatus();
                        this.addMessage('assistant', data.response || 'No response received');
                        return;
                    } else if (data.status === 'failed') {
                        this.hideStatus();
                        this.addMessage('assistant', `Error: ${data.error || 'Request failed'}`);
                        return;
                    } else {
                        // Update status
                        this.updateStatus(`Status: ${data.status}...`);
                    }
                }

                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, 2000);
                } else {
                    this.hideStatus();
                    this.addMessage('assistant', 'Request timed out. Please try again.');
                }
            } catch (error) {
                this.hideStatus();
                this.addMessage('assistant', `Error: ${error.message}`);
            }
        };

        poll();
    }

    parseMessageContent(content) {
        const parts = [];
        let currentIndex = 0;
        
        // Regular expressions for different content types
        const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
        const htmlInlineRegex = /`([^`\n]+)`/g;
        
        // Find all matches and their positions
        const matches = [];
        
        // Find code blocks first (they take precedence)
        let match;
        while ((match = codeBlockRegex.exec(content)) !== null) {
            matches.push({
                type: 'code',
                start: match.index,
                end: match.index + match[0].length,
                language: match[1] || '',
                content: match[2]
            });
        }
        
        // Find HTML inline content (single backticks), but skip if inside code blocks
        while ((match = htmlInlineRegex.exec(content)) !== null) {
            // Check if this match is inside a code block
            const isInsideCodeBlock = matches.some(codeMatch => 
                match.index >= codeMatch.start && match.index < codeMatch.end
            );
            
            if (!isInsideCodeBlock) {
                matches.push({
                    type: 'html',
                    start: match.index,
                    end: match.index + match[0].length,
                    content: match[1]
                });
            }
        }
        
        // Sort matches by start position
        matches.sort((a, b) => a.start - b.start);
        
        // Extract text parts between matches
        matches.forEach((match) => {
            // Add text before this match
            if (currentIndex < match.start) {
                const textContent = content.substring(currentIndex, match.start);
                if (textContent.trim()) {
                    parts.push({
                        type: 'text',
                        content: textContent
                    });
                }
            }
            
            // Add the match
            parts.push(match);
            currentIndex = match.end;
        });
        
        // Add remaining text after last match
        if (currentIndex < content.length) {
            const textContent = content.substring(currentIndex);
            if (textContent.trim()) {
                parts.push({
                    type: 'text',
                    content: textContent
                });
            }
        }
        
        // If no matches found, return the whole content as text
        if (parts.length === 0) {
            parts.push({
                type: 'text',
                content: content
            });
        }
        
        return parts;
    }

    sanitizeHtml(html) {
        // Basic HTML sanitization - allows common safe tags
        const allowedTags = {
            'p': true, 'br': true, 'strong': true, 'b': true, 'em': true, 'i': true,
            'u': true, 'span': true, 'div': true, 'h1': true, 'h2': true, 'h3': true,
            'h4': true, 'h5': true, 'h6': true, 'ul': true, 'ol': true, 'li': true,
            'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height'],
            'table': true, 'tr': true, 'td': true, 'th': true, 'thead': true, 'tbody': true,
            'code': true, 'pre': true, 'blockquote': true
        };
        
        // Create a temporary div to parse HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Recursively clean the HTML
        const cleanElement = (element) => {
            if (element.nodeType === Node.TEXT_NODE) {
                return element.textContent;
            }
            
            if (element.nodeType !== Node.ELEMENT_NODE) {
                return '';
            }
            
            const tagName = element.tagName.toLowerCase();
            const allowedAttributes = allowedTags[tagName];
            
            if (!allowedAttributes) {
                // Tag not allowed, return text content only
                return element.textContent;
            }
            
            // Create new clean element
            const cleanEl = document.createElement(tagName);
            
            // Copy allowed attributes
            if (Array.isArray(allowedAttributes)) {
                allowedAttributes.forEach(attr => {
                    const attrValue = element.getAttribute(attr);
                    if (attrValue) {
                        // Additional security for href and src
                        if (attr === 'href' && !attrValue.match(/^(https?:|mailto:|#)/)) {
                            return; // Skip unsafe URLs
                        }
                        if (attr === 'src' && !attrValue.match(/^(https?:|data:image)/)) {
                            return; // Skip unsafe image sources
                        }
                        cleanEl.setAttribute(attr, attrValue);
                    }
                });
            }
            
            // Process children recursively
            Array.from(element.childNodes).forEach(child => {
                if (child.nodeType === Node.TEXT_NODE) {
                    cleanEl.appendChild(document.createTextNode(child.textContent));
                } else if (child.nodeType === Node.ELEMENT_NODE) {
                    const cleanChild = cleanElement(child);
                    if (typeof cleanChild === 'string') {
                        cleanEl.appendChild(document.createTextNode(cleanChild));
                    } else {
                        cleanEl.appendChild(cleanChild);
                    }
                }
            });
            
            return cleanEl;
        };
        
        const cleanedElements = Array.from(tempDiv.childNodes).map(cleanElement);
        const result = document.createElement('div');
        cleanedElements.forEach(el => {
            if (typeof el === 'string') {
                result.appendChild(document.createTextNode(el));
            } else {
                result.appendChild(el);
            }
        });
        
        return result.innerHTML;
    }

    createBubble(part, sender, isFirst = false, isLast = false) {
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${part.type}`;
        
        // Add positioning classes for multiple bubbles
        if (!isFirst && !isLast) {
            bubble.classList.add('bubble-middle');
        } else if (!isFirst) {
            bubble.classList.add('bubble-last');
        } else if (!isLast) {
            bubble.classList.add('bubble-first');
        }
        
        switch (part.type) {
            case 'text':
                bubble.textContent = part.content;
                break;
                
            case 'html':
                try {
                    const sanitizedHtml = this.sanitizeHtml(part.content);
                    bubble.innerHTML = sanitizedHtml;
                    bubble.classList.add('html-content');
                } catch (error) {
                    console.warn('Failed to render HTML content:', error);
                    bubble.textContent = part.content;
                }
                break;
                
            case 'code':
                const preElement = document.createElement('pre');
                const codeElement = document.createElement('code');
                
                if (part.language) {
                    codeElement.className = `language-${part.language}`;
                    preElement.classList.add('line-numbers');
                }
                
                codeElement.textContent = part.content;
                preElement.appendChild(codeElement);
                
                // Add language label if specified
                if (part.language) {
                    const langLabel = document.createElement('div');
                    langLabel.className = 'code-language-label';
                    langLabel.textContent = part.language;
                    bubble.appendChild(langLabel);
                }
                
                bubble.appendChild(preElement);
                bubble.classList.add('code-content');
                
                // Apply syntax highlighting after DOM insertion
                setTimeout(() => {
                    if (window.Prism) {
                        Prism.highlightElement(codeElement);
                    }
                }, 0);
                break;
        }
        
        return bubble;
    }

    addMessage(sender, content, timestamp = null) {
        // Parse the message content into different parts
        const parts = this.parseMessageContent(content);
        
        // Create the main message container
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        // Create avatar (only for the first bubble)
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'C';
        messageDiv.appendChild(avatar);
        
        // Create a container for all bubbles
        const bubblesContainer = document.createElement('div');
        bubblesContainer.className = 'message-bubbles';
        
        // Create bubbles for each part
        parts.forEach((part, index) => {
            const isFirst = index === 0;
            const isLast = index === parts.length - 1;
            const bubble = this.createBubble(part, sender, isFirst, isLast);
            
            // Add timestamp to the last bubble if provided
            if (timestamp && isLast) {
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-timestamp';
                timeDiv.style.cssText = 'font-size: 0.75em; color: #6c757d; margin-top: 5px; opacity: 0.7;';
                const date = new Date(timestamp);
                timeDiv.textContent = date.toLocaleString();
                bubble.appendChild(timeDiv);
            }
            
            bubblesContainer.appendChild(bubble);
        });
        
        messageDiv.appendChild(bubblesContainer);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    clearChat() {
        this.chatMessages.innerHTML = '';
    }

    showStatus(text) {
        this.statusText.textContent = text;
        this.statusIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    updateStatus(text) {
        this.statusText.textContent = text;
    }

    hideStatus() {
        this.statusIndicator.style.display = 'none';
    }

    scrollToBottom() {
        // Use requestAnimationFrame for smoother scrolling on mobile
        requestAnimationFrame(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            // Add small delay for mobile rendering
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 50);
        });
    }
    
    initializeMobileHandling() {
        // Only add mobile keyboard handling if on mobile device
        if (window.innerWidth <= 768) {
            // Visual viewport API for better keyboard handling
            if (window.visualViewport) {
                const handleViewportChange = () => {
                    const currentHeight = window.visualViewport.height;
                    const heightDiff = this.initialViewportHeight - currentHeight;
                    
                    // Detect keyboard open/close
                    if (heightDiff > 150) { // Keyboard is likely open
                        if (!this.keyboardOpen) {
                            this.keyboardOpen = true;
                            this.scrollPosition = document.documentElement.scrollTop || document.body.scrollTop;
                        }
                    } else { // Keyboard is likely closed
                        if (this.keyboardOpen) {
                            this.keyboardOpen = false;
                            // Restore scroll position after a short delay
                            setTimeout(() => {
                                if (this.scrollPosition > 0) {
                                    window.scrollTo(0, this.scrollPosition);
                                } else {
                                    // Scroll to top if no previous position
                                    window.scrollTo(0, 0);
                                }
                            }, 150);
                        }
                    }
                };
                
                window.visualViewport.addEventListener('resize', handleViewportChange);
            } else {
                // Fallback for older browsers
                let initialHeight = window.innerHeight;
                
                const handleResize = () => {
                    const currentHeight = window.innerHeight;
                    const heightDiff = initialHeight - currentHeight;
                    
                    if (heightDiff > 150) {
                        if (!this.keyboardOpen) {
                            this.keyboardOpen = true;
                            this.scrollPosition = document.documentElement.scrollTop || document.body.scrollTop;
                        }
                    } else {
                        if (this.keyboardOpen) {
                            this.keyboardOpen = false;
                            setTimeout(() => {
                                if (this.scrollPosition > 0) {
                                    window.scrollTo(0, this.scrollPosition);
                                } else {
                                    window.scrollTo(0, 0);
                                }
                            }, 150);
                        }
                    }
                };
                
                window.addEventListener('resize', handleResize);
            }
        }
    }
    
    handleInputFocus() {
        // Store scroll position before keyboard opens
        if (window.innerWidth <= 768) {
            this.scrollPosition = document.documentElement.scrollTop || document.body.scrollTop;
            // Scroll chat to bottom when input is focused to ensure visibility
            setTimeout(() => {
                this.scrollToBottom();
            }, 100);
        }
    }
    
    handleInputBlur() {
        // Handle input blur on mobile
        if (window.innerWidth <= 768) {
            // Small delay to ensure keyboard is fully closed
            setTimeout(() => {
                if (!this.keyboardOpen) {
                    // Restore scroll position if keyboard is closed
                    if (this.scrollPosition > 0) {
                        window.scrollTo(0, this.scrollPosition);
                    } else {
                        window.scrollTo(0, 0);
                    }
                    // Ensure chat messages stay scrollable
                    this.scrollToBottom();
                }
            }, 300);
        }
    }

    async createProject() {
        const name = prompt('Enter project name:');
        if (!name) return;

        try {
            const response = await fetch(`${this.apiBase}/project/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name })
            });

            const data = await response.json();
            if (data.success) {
                await this.loadProjects();
                await this.selectProject(data.project_name);
            } else {
                alert(`Failed to create project: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async deleteProject() {
        if (!this.currentProject) return;
        
        if (!confirm(`Delete project "${this.currentProject}"? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/project/${this.currentProject}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (data.success) {
                this.currentProject = null;
                this.currentThread = null;
                localStorage.removeItem('lastProject');
                localStorage.removeItem('lastThread');
                
                await this.loadProjects();
                this.clearChat();
                this.addMessage('assistant', 'Project deleted. Create or select another project to continue.');
                
                // Disable buttons
                this.deleteProjectBtn.disabled = true;
                this.newThreadBtn.disabled = true;
                this.deleteThreadBtn.disabled = true;
                this.sendBtn.disabled = true;
            } else {
                alert(`Failed to delete project: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async createThread() {
        if (!this.currentProject) return;

        const name = prompt('Enter thread name (optional):');
        
        try {
            const response = await fetch(`${this.apiBase}/project/${this.currentProject}/thread/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: name || undefined })
            });

            const data = await response.json();
            if (data.success) {
                await this.loadProjects();
                await this.navigateToThread(this.currentProject, data.thread_id);
            } else {
                alert(`Failed to create thread: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async deleteThread() {
        if (!this.currentProject || !this.currentThread) return;
        
        if (!confirm(`Delete thread "${this.currentThread}"? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/project/${this.currentProject}/thread/${this.currentThread}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (data.success) {
                this.currentThread = null;
                localStorage.removeItem('lastThread');
                
                // Clear URL hash
                history.replaceState(null, '', window.location.pathname + window.location.search);
                
                await this.loadProjects();
                this.clearChat();
                this.addMessage('assistant', 'Thread deleted. Create or select another thread to continue.');
                
                // Disable thread-specific buttons
                this.deleteThreadBtn.disabled = true;
                this.sendBtn.disabled = true;
            } else {
                alert(`Failed to delete thread: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    createFileTreeItem(label, type, path, hasChildren = false) {
        const li = document.createElement('li');
        li.className = 'tree-item';
        
        if (type === 'directory') {
            // Directory - use div with click handler
            const content = document.createElement('div');
            content.className = 'tree-item-content';
            content.dataset.type = type;
            content.dataset.path = path;
            
            if (hasChildren) {
                const icon = document.createElement('span');
                icon.className = 'tree-icon';
                icon.textContent = '▶';
                content.appendChild(icon);
                
                content.addEventListener('click', (e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    this.toggleFileTreeItem(li);
                });
                content.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    // Prevent unwanted input focus
                    if (document.activeElement && document.activeElement.blur) {
                        document.activeElement.blur();
                    }
                    this.toggleFileTreeItem(li);
                });
            }
            
            const labelSpan = document.createElement('span');
            labelSpan.className = 'tree-label';
            labelSpan.textContent = label;
            content.appendChild(labelSpan);
            
            li.appendChild(content);
        } else {
            // File - use proper URL link that opens in new tab
            const link = document.createElement('a');
            link.className = 'tree-item-content file-link';
            link.href = `${this.apiBase}/view/${this.currentProject}/file/${path}`;
            link.target = '_blank';  // Open in new tab
            link.dataset.type = type;
            link.dataset.path = path;
            link.style.cssText = 'text-decoration: none; color: inherit; display: flex; align-items: center;';
            
            const labelSpan = document.createElement('span');
            labelSpan.className = 'tree-label';
            labelSpan.textContent = label;
            link.appendChild(labelSpan);
            
            li.appendChild(link);
        }
        
        return li;
    }

    toggleFileTreeItem(li) {
        const icon = li.querySelector('.tree-icon');
        const children = li.querySelector('.tree-children');
        
        if (children) {
            if (children.style.display === 'none' || !children.style.display) {
                children.style.display = 'block';
                icon.textContent = '▼';
            } else {
                children.style.display = 'none';
                icon.textContent = '▶';
            }
        }
    }


    async loadThreadMessages(threadId) {
        try {
            const response = await fetch(`${this.apiBase}/project/${this.currentProject}/thread/${threadId}/messages`);
            const data = await response.json();
            
            if (data.success && data.messages && data.messages.length > 0) {
                // Load existing messages
                data.messages.forEach(message => {
                    this.addMessage(message.role, message.content, message.timestamp);
                });
            } else {
                // No messages yet, show welcome message
                this.addMessage('assistant', `Thread "${threadId}" selected. You can now start chatting!`);
            }
        } catch (error) {
            console.error('Failed to load thread messages:', error);
            this.addMessage('assistant', `Thread "${threadId}" selected. You can now start chatting!`);
        }
    }
}

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ClaudeWebApp();
});

// Prevent pull-to-refresh on mobile (more targeted approach)
document.body.addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) return;
    
    const touch = e.touches[0];
    const isAtTop = document.documentElement.scrollTop === 0 || document.body.scrollTop === 0;
    
    // Only prevent pull-to-refresh when actually at top and pulling down significantly
    if (isAtTop && touch.clientY > 100) {
        // Check if this is actually a pull-down gesture by checking target
        const target = e.target;
        if (!target.closest('.input-field') && 
            !target.closest('button') && 
            !target.closest('a') &&
            !target.closest('.tree-item-content') &&
            !target.closest('.chat-messages') &&
            !target.closest('.sidebar-content')) {
            e.preventDefault();
        }
    }
}, { passive: false });

// Additional mobile optimizations (much more permissive)
document.body.addEventListener('touchmove', (e) => {
    const element = e.target;
    
    // Always allow scrolling in chat and sidebar areas
    if (element.closest('.chat-messages') || 
        element.closest('.sidebar-content') || 
        element.closest('.input-field') ||
        element.closest('.tree-view')) {
        return; // Allow all natural scrolling
    }
    
    // Allow button and link interactions
    if (element.closest('button') ||
        element.closest('a') ||
        element.closest('.tree-item-content')) {
        return; // Allow all interactions
    }
    
    // Only prevent bounce scrolling when overlay is active AND we're sure it's needed
    const overlay = document.getElementById('overlay');
    if (overlay && overlay.classList.contains('show')) {
        const isAtTop = document.documentElement.scrollTop <= 0;
        const isAtBottom = (window.innerHeight + document.documentElement.scrollTop) >= document.documentElement.offsetHeight - 5;
        
        // Only prevent at very specific edge cases to avoid bounce
        if ((isAtTop && e.touches[0].pageY > e.touches[0].startY) || 
            (isAtBottom && e.touches[0].pageY < e.touches[0].startY)) {
            e.preventDefault();
        }
    }
}, { passive: false });