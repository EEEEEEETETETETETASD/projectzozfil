def check_update():
    try:
        import git
        repo = git.Repo('.')
        repo.remotes.origin.pull()
        print("Game updated successfully.")
    except Exception as e:
        print(f"Update check failed: {e}")

if __name__ == "__main__":
    check_update()