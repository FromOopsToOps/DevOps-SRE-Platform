# Git Workflow Guide

This guide outlines a simple and professional Git workflow. Follow the steps below to clone a repository, create a new branch, commit your work, and open a pull request.
Being honest, that's 90% of what you'll need on a daily basis.

---

## 1. install git, gh and authenticate them

For MacOS:
```bash
brew install git
brew install gh
gh auth login
```

This will help you authenticate gh (github CLI, so you can manage things from cli) and git (operate repositories).
gh isn't as straitghforward to configure, so this is a sample of what happens and what you should answer:

```
▶ gh auth login
? Where do you use GitHub? 
GitHub.com <---
? What is your preferred protocol for Git operations on this host? 
SSH <---
? Upload your SSH public key to your GitHub account? 
/Users/rafael.umbelino/.ssh/id_ed25519.pub <---
? Title for your SSH key: 
homedepot <---
? How would you like to authenticate GitHub CLI? 
Login with a web browser <---

! First copy your one-time code: 9076-9F57
Press Enter to open https://github.com/login/device in your browser...
```

Then, press enter. It will start or open a new tab on your browser, click on authorize there. Paste the one-time code on the page.

```
✓ Authentication complete.
- gh config set -h github.com git_protocol ssh
✓ Configured git protocol
✓ SSH key already existed on your GitHub account: /Users/rafael.umbelino/.ssh/id_ed25519.pub
✓ Logged in as YOURGITUSER
! You were already logged in to this account
```

---

## 2. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/your-organization/repo.git
cd repo
```

You can clone like this for HTTPS but you should be using SSH! Please configure your SSH auth on your github.
Replace the URL with your repository’s actual address. Cloning with SSH looks like this:

```bash
git clone git@github.com:org/repo.git
cd repo
```

---

## 3. Create a New Branch from `main`

Always work on a separate branch to keep `main` stable:

```bash
git checkout -b new-branch main
```

Use a descriptive name that reflects the purpose of your changes.

---

## 4. See What Has Changed

To review your changes since the last pull or commit:

```bash
git diff
```

To check which files are modified or staged:

```bash
git status
```

---

## 5. Stage Your Changes

Stage all modified files:

```bash
git add *
```

Or stage specific files:

```bash
git add path/to/file
```

---

## 6. Write a Meaningful Commit Message

Commit messages should be clear and specific:

```bash
git commit -m "Adding an initial documentation on how to use git"
```

**Tips for commit messages:**
- Use imperative mood (e.g., "Add", "Fix", "Update")
- Keep the message concise and focused

---

## 7. Push to Your Branch

Push your branch to the remote repository:

```bash
git push -u origin documentation
```

---

## 8. Create a Pull Request

execute this substituting the information:

```
gh pr create --base main --head documentation --title "Creating a documentation" --body "Starting up a knowledge database for the team on how to use stuff and do work."
                    /\          /\
```
In '--base' use the main branch (sometimes it has a different name, pay attention!) and in '--head' use the name of the branch you just created! 

---

## Notes

- Keep pull requests focused on a single topic.
- Regularly pull updates from `main` to avoid conflicts.
- Ask for a review once your work is ready.