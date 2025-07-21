// test/cmd.test.mjs

import chai from 'chai';
import sinon from 'sinon'; // For mocking
const expect = chai.expect;

// Import the function to be tested
import { parseDleHandler } from '../cmd.mjs'; // Adjust path if needed

// Import modules that parseDleHandler depends on, for mocking purposes
// You need to import them to replace their methods with stubs/spies
import * as createOutDirectoryModule from '../createOutDirectory.mjs';
import * as logmessageModule from '../logs/info.mjs';
import * as validateDirectoriesModule from '../utils/validation/directories.mjs';
import * as validateInputModule from '../utils/input/validateInput.mjs';
import * as dleFilesModule from '../utils/dle/index.mjs'; // Contains getUnparsedDleFiles, getParsedWorkbook
import * as profilesModule from '../utils/choices/profiles.mjs';
import * as parserModule from '../parser.mjs'; // Contains parseDles
import * as configModule from '../config/config.mjs';
import store from '../store/index.mjs'; // Assuming 'store' is a default export or a singleton instance

describe('parseDleHandler', () => {
    let sandbox; // Use a sandbox for managing stubs/spies

    beforeEach(() => {
        sandbox = sinon.createSandbox(); // Create a new sandbox before each test

        // --- Mocking Dependencies ---
        // Mock functions that perform side effects or external calls
        sandbox.stub(createOutDirectoryModule, 'createOutDirectory').returns(true); // Or return a Promise.resolve(true) if async
        sandbox.stub(logmessageModule, 'logmessage'); // Just ensure it's called, don't care about return
        sandbox.stub(validateDirectoriesModule, 'validateDirectories').returns(true);
        sandbox.stub(validateInputModule, 'validateInput').returns(true);
        sandbox.stub(profilesModule, 'chooseProfiles').returns('mockProfile'); // Or a specific profile object
        sandbox.stub(configModule, 'createConfig').resolves({ /* mock config object */ }); // Assuming createConfig is async

        // Mock store interactions
        sandbox.stub(store, 'dispatch');
        sandbox.stub(store, 'getState').returns({ tagmanager: { /* mock state */ } }); // Return a mock state

        // Mock the DLE file fetching/parsing
        // This is crucial: simulate what getUnparsedDleFiles or getParsedWorkbook would return
        sandbox.stub(dleFilesModule, 'getUnparsedDleFiles').resolves([
            { name: 'file1.csv', content: 'csv content 1' },
            { name: 'file2.csv', content: 'csv content 2' }
        ]);
        sandbox.stub(dleFilesModule, 'getParsedWorkbook').resolves([
            { name: 'workbook_sheet1', content: 'excel content 1' }
        ]);

        // Mock the actual DLE parsing logic
        // Simulate what parseDles would return after processing the files
        sandbox.stub(parserModule, 'parseDles').resolves([
            { name: 'parsed_dle_1', data: { key: 'value' } },
            { name: 'parsed_dle_2', data: { anotherKey: 'anotherValue' } }
        ]);
    });

    afterEach(() => {
        sandbox.restore(); // Restore all stubs/spies after each test
    });

    it('should correctly parse DLEs from a directory', async () => {
        const options = {
            environment: 'dev',
            directory: '/mock/input/dir',
            profile: 'mockProfile',
            suppressOutput: false
        };
        const program = {}; // Commander's program object, often not used directly in handler logic

        const result = await parseDleHandler(options, program);

        // Assertions
        expect(result).to.be.an('array');
        expect(result).to.have.lengthOf(2); // Based on our mock parseDles return
        expect(result[0]).to.have.property('name', 'parsed_dle_1');
        expect(result[1]).to.have.property('data');

        // Verify that specific mock functions were called as expected
        expect(createOutDirectoryModule.createOutDirectory.calledOnce).to.be.true;
        expect(logmessageModule.logmessage.calledTwice).to.be.true; // Once for each parsed DLE
        expect(dleFilesModule.getUnparsedDleFiles.calledOnce).to.be.true;
        expect(dleFilesModule.getParsedWorkbook.notCalled).to.be.true; // Because workbook option was not provided
        expect(parserModule.parseDles.calledOnceWith(
            sinon.match.array, // Expects an array (dleCvsList)
            options.environment,
            options.directory,
            options.profile,
            options.suppressOutput
        )).to.be.true;

        // Verify store interactions
        expect(store.dispatch.calledWith(sinon.match({ type: 'TAGMANAGER_ADD_CONFIG' }))).to.be.true;
        expect(store.dispatch.calledWith(sinon.match({ type: 'TAGMANAGER_SET_STATE' }))).to.be.true;
    });

    it('should correctly parse DLEs from an Excel workbook', async () => {
        const options = {
            environment: 'prod',
            workbook: 'C:\\mock\\test.xlsx', // Provide workbook path
            profile: 'mockProfile',
            suppressOutput: true // Suppress output for this test
        };
        const program = {};

        const result = await parseDleHandler(options, program);

        expect(result).to.be.an('array');
        expect(result).to.have.lengthOf(2); // Still based on parseDles mock

        expect(dleFilesModule.getParsedWorkbook.calledOnceWith(options.workbook)).to.be.true;
        expect(dleFilesModule.getUnparsedDleFiles.notCalled).to.be.true; // Because workbook option was provided

        // logmessage should not be called if suppressOutput is true
        expect(logmessageModule.logmessage.notCalled).to.be.true;
    });

    it('should return an empty array if no DLE files are found', async () => {
        // Override the mock for this specific test
        dleFilesModule.getUnparsedDleFiles.resolves([]);
        dleFilesModule.getParsedWorkbook.resolves([]); // Also for workbook case

        const options = {
            environment: 'dev',
            directory: '/mock/empty/dir',
            profile: 'mockProfile',
            suppressOutput: false
        };
        const program = {};

        const result = await parseDleHandler(options, program);

        expect(result).to.be.an('array').that.is.empty;
        expect(parserModule.parseDles.notCalled).to.be.true; // parseDles should not be called
        expect(logmessageModule.logmessage.notCalled).to.be.true; // No DLEs to log
    });

    it('should handle errors during DLE parsing', async () => {
        // Override the mock to simulate an error
        parserModule.parseDles.rejects(new Error('Simulated parsing error'));

        const options = {
            environment: 'dev',
            directory: '/mock/input/dir',
            profile: 'mockProfile',
            suppressOutput: false
        };
        const program = {};

        // Expect the handler to throw an error
        await expect(parseDleHandler(options, program)).to.be.rejectedWith('Simulated parsing error');
    });

    // Add more test cases for different scenarios, edge cases, and error conditions
});
