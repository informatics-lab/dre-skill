# dre
Decision Recommendation Engine

### Set-up
Here is the recipie to set up and develop this repo. You need Grunt, NPM, Pip and [nose](https://nose.readthedocs.org/en/latest/) 

1. `git clone` this repo
2. `npm install`

To test the repo run `grunt test`

To deploy to AWS Lambda

1. Edit/create your credentials in `~/.aws/credentials`
2. Add an entry like this
```
[dre]
aws_access_key_id=<A RELEVANT THING>
aws_secret_access_key=<A RELEVANT THING>
```

3. Run `grunt deploy`
