var grunt = require('grunt');
grunt.loadNpmTasks('grunt-aws-lambda');
grunt.loadNpmTasks('grunt-shell');

grunt.initConfig({
    lambda_deploy: {
        default: {
            arn: 'arn:aws:lambda:us-east-1:536099501702:function:moDRE',
        options: {
                profile: "dre"
            }
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