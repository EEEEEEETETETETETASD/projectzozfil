import git

def push_update():
    try:
        repo = git.Repo('.')
        repo.git.add('.')
        repo.index.commit("Update game")
        repo.remotes.origin.push()
        print("Update pushed to GitHub.")
    except Exception as e:
        print(f"Push failed: {e}")

if __name__ == "__main__":
    push_update()