// ======================= image upload =======================


function openImageUploadPopup() {
    document.getElementById("image-upload-popup").style.display = "block";
}

function closeImageUploadPopup() {
    document.getElementById("image-upload-popup").style.display = "none";
}

function setProfileImage() {
    const input = document.getElementById("popup-image-input");
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById("profile-pic-preview").src = e.target.result;
        }
        reader.readAsDataURL(input.files[0]);

        // Set this image to the hidden file input in the actual form
        const fileInput = document.getElementById("profile_pic_input");
        fileInput.files = input.files;

        closeImageUploadPopup();
    } else {
        alert("Please select an image.");
    }
}

// ======================= Aadhaar Validation =======================
function formatAadhaar(input) {
    let value = input.value.replace(/\D/g, ''); 
    let formattedValue = value.replace(/(\d{4})(?=\d)/g, '$1 ').trim(); 
    input.value = formattedValue;
}

const verhoeffTableD = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,2,3,4,0,6,7,8,9,5],
    [2,3,4,0,1,7,8,9,5,6],
    [3,4,0,1,2,8,9,5,6,7],
    [4,0,1,2,3,9,5,6,7,8],
    [5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2],
    [7,6,5,9,8,2,1,0,4,3],
    [8,7,6,5,9,3,2,1,0,4],
    [9,8,7,6,5,4,3,2,1,0]
];

const verhoeffTableP = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,5,7,6,2,8,3,0,9,4],
    [5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7],
    [9,4,5,3,1,2,6,8,7,0],
    [4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],
    [7,0,4,6,9,1,3,2,5,8]
];

function verhoeffValidate(num) {
    let c = 0;
    let numArr = num.split("").reverse().map(Number);
    for (let i = 0; i < numArr.length; i++) {
        c = verhoeffTableD[c][verhoeffTableP[i % 8][numArr[i]]];
    }
    return c === 0;
}

function validateAadhaar() {
    let aadhaarInput = document.getElementById("aadhaar").value.replace(/\s/g, '');
    let errorSpan = document.getElementById("aadhaar-error");

    if (!aadhaarInput) {
        errorSpan.textContent = "❌ Aadhaar number is required.";
        errorSpan.style.color = "red";
        return;
    }

    if (!verhoeffValidate(aadhaarInput)) {
        errorSpan.textContent = "❌ Invalid Aadhaar number.";
        errorSpan.style.color = "red";
        return;
    }

    fetch(`/check_all/?aadhaar=${aadhaarInput}`)
        .then(response => {
            if (!response.ok) throw new Error("Network error");
            return response.json();
        })
        .then(data => {
            if (data.exists) {
                errorSpan.textContent = "❌ This Aadhaar number is already registered.";
                errorSpan.style.color = "red";
            } else {
                errorSpan.textContent = "✅ Aadhaar is valid!";
                errorSpan.style.color = "green";
            }
            if (typeof checkForm === "function") checkForm(); // optional form checker
        })
        .catch(error => {
            console.error("Error checking Aadhaar:", error);
            errorSpan.textContent = "❌ Error validating Aadhaar.";
            errorSpan.style.color = "red";
        });
}
// ======================= Auto Detect Location 1 =======================
// Function to get user's exact location

document.addEventListener("DOMContentLoaded", function () {
    alert("Please allow location access to fetch your current location.");
    getUserLocation();
});

function getUserLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            document.getElementById("latitude").value = lat;
            document.getElementById("longitude").value = lon;

            // Use OpenStreetMap reverse geocoding
            const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.address) {
                        const address = data.display_name || "";
                        const state = data.address.state || "";
                        const district = data.address.state_district || data.address.county || "";
                        const city = data.address.city || data.address.town || data.address.village || "";

                        document.getElementById("address").value = address;
                        document.getElementById("state").value = state;
                        document.getElementById("district").value = district;
                        document.getElementById("city").value = city;
                    } else {
                        alert("Unable to fetch address. Please try again.");
                    }
                })
                .catch(error => {
                    console.error("Error fetching address:", error);
                    alert("Error fetching location details. Please check your internet/GPS.");
                });
        },
        function (error) {
            let errorMsg = "Unable to fetch location.";
            if (error.code === error.PERMISSION_DENIED) {
                errorMsg = "Location access denied. Please enable GPS.";
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                errorMsg = "Location unavailable.";
            } else if (error.code === error.TIMEOUT) {
                errorMsg = "Location request timed out.";
            }
            alert(errorMsg);
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
}

function reloadLocation() {
    alert("Refreshing location. Please ensure GPS is enabled.");
    getUserLocation();
}


