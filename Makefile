.PHONY: issue

issue:
	@printf "Issue Title: "; \
	read title; \
	filename=$$(echo "$$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-'); \
	filepath="issues/00_BACKLOG/$$filename.md"; \
	cp issues/TEMPLATE.md "$$filepath"; \
	sed -i '' "s/\[Title\]/$$title/" "$$filepath"; \
	echo "Created issue: $$filepath"

# Google Cloud Authentication
.PHONY: auth login set-project

PROJECT_ID ?= enikki-cloud

login:
	gcloud auth application-default login

set-project:
	gcloud config set project $(PROJECT_ID)
	gcloud auth application-default set-quota-project $(PROJECT_ID)

auth: login set-project
	@echo "Authentication setup complete for project: $(PROJECT_ID)"
