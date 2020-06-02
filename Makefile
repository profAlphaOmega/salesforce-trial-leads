SERVICE := mrkt-salesforce-leads

ifeq ($(ENV),)
$(error ENV needs to be defined. e.g.: make deploy ENV=dev)
endif

build:
	docker build -t $(SERVICE) .

run: build
	docker run -it -p 8080:8080 $(SERVICE)

deploy:
#check to see if there is a constants file???
	gcloud app deploy app.$(ENV).yaml --project=redacted --version=$(shell date +%Y%m%d-%H%M)

logs:
	gcloud app logs tail \
		--service=$(SERVICE) \
		--version=`gcloud app instances list --project=redacted | grep $(SERVICE) | awk '{print $$2}'` \
		--project=v1-dev-main \
		| grep -v '/health-check'
