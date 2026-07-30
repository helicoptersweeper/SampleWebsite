const form = document.getElementById("reportForm");
const status = document.getElementById("status");

form.addEventListener("submit", function (event) {

    event.preventDefault();

    const report = {
        report_type: document.getElementById("type").value,
        report_text: document.getElementById("text").value,
        latitude: null,
        longitude: null
    };

    if (!navigator.geolocation) {
        submitReport(report);
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function (position) {

            report.latitude = position.coords.latitude;
            report.longitude = position.coords.longitude;

            submitReport(report);

        },

        function () {

            // User denied permission or location unavailable.
            // Keep latitude/longitude as null.
            submitReport(report);

        }

    );

});


async function submitReport(report) {

    status.textContent = "Submitting...";

    try {

        const response = await fetch("/report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(report)
        });

        const result = await response.json();

        status.textContent = result.message;

        setTimeout(() => {
            document.location = "/";
        }, 1000);

    } catch (err) {

        console.error(err);
        status.textContent = "Failed to submit report.";

    }

}