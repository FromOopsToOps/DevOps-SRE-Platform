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
You can also replace github.com with the name of the SSH key you're using (according to your .ssh/config file).

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
git add .*
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

---

# Managing Multiple GitHub Identities on One Machine (Personal + Work)

Let’s face it: many of us wear **two GitHub hats** — one for personal projects, one for work.
On the same laptop. Every day.
And if you’ve ever almost pushed a weekend side-project commit into your company’s monorepo… you know why this matters.

Here’s how to set up **multiple SSH identities** so your `git push` always goes to the right place, without constantly typing `gh auth login`.

## 1. Generate Two SSH Keys

```bash
ssh-keygen -t ed25519 -C "personal" -f ~/.ssh/Personal
ssh-keygen -t ed25519 -C "work" -f ~/.ssh/Work

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/Personal ~/.ssh/Work
```

## 2. Configure `~/.ssh/config`

```sshconfig
Host PersonalGit
  HostName github.com
  User git
  IdentityFile ~/.ssh/Personal
  IdentitiesOnly yes

Host WorkGit
  HostName github.com
  User git
  IdentityFile ~/.ssh/Work
  IdentitiesOnly yes
```

Now when you use `git@PersonalGit:username/repo.git`, SSH knows to use your **Personal** key.
For work: `git@WorkGit:org/repo.git`.

## 3. Add Keys to GitHub via `gh`

For personal account (while logged in as personal):

```bash
gh ssh-key add ~/.ssh/Personal.pub --title "Personal laptop"
```

Then switch login (or use a PAT) for work account and run:

```bash
gh ssh-key add ~/.ssh/Work.pub --title "Work laptop"
```

## 4. Create and Push to a Sample Repo (Personal)

```bash
gh repo create PersonalGit/multi-ssh-demo --public -y

mkdir example-folder && cd example-folder
git init -b main
echo "Example Content" > README.md
git add README.md
git commit -m "Initial commit"

git remote add origin git@PersonalGit:PersonalGit/multi-ssh-demo.git
git push -u origin main

# open in browser to check
gh repo view PersonalGit/multi-ssh-demo --web
```

## 5. Cleanup

```bash
gh repo delete PersonalGit/multi-ssh-demo --confirm
cd ..
rm -rf example-folder
```

## Day-to-Day Usage

- For personal repos:  
```bash
git clone git@PersonalGit:username/repo.git
```

- For work repos:  
```bash
git clone git@WorkGit:org/repo.git
```

Pro tip: teach this to your team’s juniors; it saves everyone support headaches later.