#!/usr/bin/env bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if there are staged changes
if ! git diff --cached --quiet; then
    echo -e "${GREEN}Staged changes detected.${NC}"
else
    echo -e "${RED}No staged changes found. Please stage your changes first.${NC}"
    exit 1
fi

# Function to generate commit message
generate_commit_message() {
	local continue_session="$1"
    local context="${2:-}"
    local prompt="Based on the following git diff of staged changes, generate a conventional commit message with a clear subject line (max 72 chars) and body (wrapped at 72 chars). The message should clearly explain what changed and why."
    
    if [ -n "$context" ]; then
        prompt="$prompt Additional context from user: $context"
    fi
    
    # Use -c flag for regenerate to maintain session
    local claude_cmd="claude"
    if [ "$continue_session" = "true" ]; then
        claude_cmd="claude --continue"
	else
        claude_cmd="claude"
    fi

    # Get the staged diff and generate commit message
    git diff --cached | $claude_cmd --print "$prompt

Format the commit message as plain text (no markdown):
- First line: conventional commit format (feat:, fix:, docs:, etc.) under 72 chars in English
- Empty line
- Body: wrapped at 72 chars, explaining what and why in Korean

Output only the commit message, no code blocks or formatting."
}

# Function to display commit message
display_commit_message() {
    echo -e "\n${BLUE}Generated commit message:${NC}"
    echo -e "${YELLOW}----------------------------------------${NC}"
    echo "$1"
    echo -e "${YELLOW}----------------------------------------${NC}\n"
}

# Main loop
while true; do
    # Generate initial commit message
    echo -e "${GREEN}Generating commit message...${NC}"
    commit_message=$(generate_commit_message "false")
    
    if [ -z "$commit_message" ]; then
        echo -e "${RED}Failed to generate commit message.${NC}"
        exit 1
    fi
    
    display_commit_message "$commit_message"
    
    # User interaction loop
    while true; do
        echo -e "${GREEN}Options:${NC}"
        echo "  a) Accept and commit"
        echo "  r [context]) Regenerate message (optionally with context)"
        echo "  q) Quit without committing"
        echo
        read -p "Your choice: " -r input
        
        # Parse the input more robustly
        # Extract the first word as choice
        choice=$(echo "$input" | awk '{print $1}')
        
        # Extract everything after the first space as context
        # Use bash regex (requires bash 3.0+) to preserve the exact input
        # The regex allows optional leading whitespace before 'r' or 'R'
        if [[ "$input" =~ ^[[:space:]]*[rR][[:space:]]+(.+)$ ]]; then
            context="${BASH_REMATCH[1]}"
        else
            context=""
        fi
        
        case $choice in
            a|A)
                echo -e "\n${GREEN}Creating commit...${NC}"
                if git commit -m "$commit_message" ; then
                    echo -e "${GREEN}Commit created successfully!${NC}"
                else
                    echo -e "${RED}Failed to create commit.${NC}"
                fi
                exit 0
                ;;
            r|R)
                echo -e "\n${GREEN}Regenerating commit message...${NC}"
                if [ -n "$context" ]; then
                    echo -e "${BLUE}With context: $context${NC}"
                fi
                commit_message=$(generate_commit_message "true" "$context")
                
                if [ -z "$commit_message" ]; then
                    echo -e "${RED}Failed to generate commit message.${NC}"
                    continue
                fi
                
                display_commit_message "$commit_message"
                ;;
            q|Q)
                echo -e "${YELLOW}Exiting without committing.${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice. Please enter 'a', 'r [context]', or 'q'.${NC}\n"
                ;;
        esac
    done
done
