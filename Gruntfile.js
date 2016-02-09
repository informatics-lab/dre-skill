var grunt = require('grunt');
var fs = require('fs');
grunt.loadNpmTasks('grunt-aws-lambda');
grunt.loadNpmTasks('grunt-shell');

if (fs.existsSync(process.env.HOME+"/.aws/credentials")) {
    theseOptions = {profile: "dre"};
    console.log("using AWS credentials file")
} else {
    // if credentials file doesn't exists (presumes using environmental variables
    theseOptions = null;
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
            command: 'nosetests ./tests/'
        }
    }
});

grunt.registerTask('deps', ['shell:pip']);
grunt.registerTask('test', ['deps', 'shell:pytest']);
grunt.registerTask('quicktest', ['shell:pytest']);
grunt.registerTask('quickdeploy', ['lambda_package', 'lambda_deploy']);
grunt.registerTask('deploy', ['test', 'lambda_package', 'lambda_deploy']);