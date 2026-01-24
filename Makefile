.PHONY: issue

issue:
	@printf "Issue Title: "; \
	read title; \
	filename=$$(echo "$$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-'); \
	filepath="issues/00_BACKLOG/$$filename.md"; \
	cp issues/TEMPLATE.md "$$filepath"; \
	sed -i '' "s/\[Title\]/$$title/" "$$filepath"; \
	echo "Created issue: $$filepath"
