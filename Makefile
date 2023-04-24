DEFAULT_GOAL := help
.PHONY: help
help: ## <Default> Display this help 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Enter virtual environment
	source .venv/bin/activate

.PHONY: install
install:
	pip install -r requirements.txt
	
.PHONY: freeze
freeze: ## Freeze requirements
	pip freeze > requirements.txt

.PHONY: inst-cdk
inst-cdk: ## Install CDK CLI
	npm i -g aws-cdk

.PHONY: aws-conf-sso
aws-conf-sso: ## Configure AWS CLI with SSO
	aws configure sso