# Bot password (name@password) comes from the environment so it never lands in git.
('wikidata', 'Frettiebot', __import__('os').environ.get('WD_BOT_PASSWORD', ''))
