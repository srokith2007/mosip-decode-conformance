package io.mosip.testrig.apirig.testrunner;

import com.aventstack.extentreports.ExtentTest;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;

public class OpenIDConformanceTest extends BaseTestCase {

    @Test
    public void runCertifyConformance() throws Exception {
        runConformance("certify");
    }

    @Test
    public void runVerifyConformance() throws Exception {
        runConformance("verify");
    }

    private void runConformance(String component) throws Exception {

        ProcessBuilder processBuilder = new ProcessBuilder(
                "python",
                "main.py",
                "--component",
                component
        );

        processBuilder.directory(
                new File(System.getProperty("user.dir"), "../../conformance-harness")
        );

        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();

        StringBuilder output = new StringBuilder();

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {

            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append(System.lineSeparator());
            }
        }

        int exitCode = process.waitFor();

        if (extent != null) {
            ExtentTest extentTest = extent.createTest(
                    "OpenID Conformance - " + component
            );
            extentTest.info(output.toString());
        }

        Assert.assertEquals(
                exitCode,
                0,
                "OpenID Conformance runner failed:\n" + output
        );
    }
}
