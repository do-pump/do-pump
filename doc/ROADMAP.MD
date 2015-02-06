# DO-PUMP Roadmap

- Feature: Yaml declaration of virtual machines to create with replica count e.t.c.
- Feature: execute on selected hosts (in complement to ssh)
- Feature: configure token
- Feature: configure VM defaults (with Yaml): 
    - ssh keys to provision, 
    - size, 
    - region, 
    - image, 
    - user data file to execute by default (should be completely overridden by command)
- Feature: set labels for vm’s and search by labels (local DB required)
- Tweak: use local DB to speedup lookups, this DB also should be synced with DO and differences should be highlighted for client
- Feature: colorization (define rules for future features)
- Refactoring: decompose logic in classes
- Bash completion script
- Package into Homebrew
- Package into .deb
- Register in pip