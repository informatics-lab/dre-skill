var grunt = require('grunt');
var fs = require('fs');
grunt.loadNpmTasks('grunt-aws-lambda');
grunt.loadNpmTasks('grunt-shell');

if (fs.existsSync(process.env.HOME+"/.aws/credentials")) {
    theseOptions = {profile: "dre"};
    console.log("using AWS credentials file")
} else {
    // if credentials file doesn't exists (presumes using environmental variables
    theseOptions = {region: "us-east-1",
                    accessKeyId: "$AWS_ACCESS_KEY_ID",
                    secretAccessKey: "$AWS_SECRET_ACCESS_KEY"};
    console.log("using AWS environmental variables")
}

grunt.initConfig({
    lambda_deploy: {
        default: {
            arn: 'arn:aws:lambda:us-east-1:536099501702:function:moDRE',
        options: theseOptions
        }
    },
    lambda_package: {
        default: {
        }
    },
    shell: {
        pip: {
            command: 'mkdir -p ./lib/ && touch ./lib/__init__.py && pip install -r requirements.txt -t ./lib/'
        },
        pytest: {
            command: 'nosetests'
        }
    }
});

grunt.registerTask('deps', ['shell:pip']);
grunt.registerTask('test', ['deps', 'shell:pytest']);
grunt.registerTask('deploy', ['test', 'lambda_package', 'lambda_deploy']);