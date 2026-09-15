fetch('/api/program/minecraft_version')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.error) {
            alert(data.error);
            return;
        }

        const versions = data.minecraft_version;

        versions.forEach(function(version) {
            document.getElementById('coreVersion').innerHTML += '<option value="' + version + '">' + version + '</option>';
        });
    });

document.querySelector('form').addEventListener('submit', function(event) {
    document.getElementById('loadingOverlay').style.display = 'flex';

    const submitButton = document.getElementById('create');
    submitButton.disabled = true;
});