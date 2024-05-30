<?php
include_once 'includes/header.php';
?>

<div class="section_left">
    <form method="POST">
        <h4 style="text-align: center;">Show the model</h4>

        <input type="text" name="refnum" value="<?php echo isset($_POST['refnum']) ? $_POST['refnum'] : '' ?>" placeholder="Specify the file name" style="width: 240px;">
        <br>



        <h4 style="text-align: center;">Validation</h4>
        <input type="radio" id="psets" name="validation" value="psets" checked>Check for missing Property sets<br>
        <input type="radio" id="arrays" name="validation" value="arrays">Check for inconsistent arrays<br>
        <input type="radio" id="dangerous" name="validation" value="dangerous">Show dangerous elements<br>
        <input type="radio" id="reused" name="validation" value="reused">Show elements that can be reused<br>
        <input type="radio" id="correctqto" name="validation" value="correctqto">Show unquantifiable elements<br>

        <button type="submit" name="show" value="show" style="width: 240px;">
            SHOW THE MODEL | RUN
        </button>
    <br><br>

    </form>

    <?php


    if (isset($_POST['show'])) {
        if ($_POST['refnum'] == "") {
            echo "Please, specify the file";
        } else {
            $model = $_POST['refnum'] . ".ifc.xkt";
            $model_py = $_POST['refnum'] . ".ifc";
            $lat = '59.9389';
            $long = '30.3157';
            $reference = 'https://maps.google.com/maps?q=' . $lat . ',' . $long . '&hl=es;z=14&amp;output=embed';
    ?>
            <!-- Trigger/Open Pop Up google map -->
            <button id="myBtn" style="width: 240px;">CHEK PROJECT LOCATION</button><br><br>

    <?php
            if (isset($_POST['validation'])) {
                if (($_POST['validation']) == "psets") {
                    $type_of_script = "checkPresenceOfPset.py 2>&1";
                }
                if (($_POST['validation']) == "arrays") {
                    $type_of_script = "checkInconsistentArrays.py 2>&1";
                }
                if (($_POST['validation']) == "dangerous") {
                    $type_of_script = "checkDangerousElements.py 2>&1";
                }
                if (($_POST['validation']) == "reused") {
                    $type_of_script = "checkReusedElements.py 2>&1";
                }
                if (($_POST['validation']) == "correctqto") {
                    $type_of_script = "checkQtoPossibility.py 2>&1";
                }
                
            }
            //echo $type_of_script;
            //echo ("<br>".$model_py);
            //$command = escapeshellcmd("$type_of_script $model_py");
            //echo (shell_exec($command));
            //echo "<br>HI";
            $outputscript = (shell_exec("$type_of_script" . $model_py));
            //echo $outputscript;

            // CALCULATING THE LOCATION AND PUSHING THE VALUES TO GOOGLE MAPS
            $location = (shell_exec("location.py 2>&1" . $model_py));
            $coords = json_decode($location);
            $lat = $coords[0];
            $long = $coords[1];
            $reference = 'https://maps.google.com/maps?q=' . $lat . ',' . $long . '&hl=es;z=14&amp;output=embed';

            /*$file = "temp/report" . $_POST['refnum'] . trim($type_of_script, "2>&1") . ".txt";
        $txt = fopen($file, "w+") or die("Unable to open file!");
        fwrite($txt, "$outputscript");
        fclose($txt);*/


            //$outputscript_guids = (shell_exec("$type_of_script_guids" . $model_py));
            //echo $outputscript_guids;
            $arr = json_decode($outputscript);

            $data1 = array();
            foreach ($arr[0] as $data) {
                array_push($data1, '"' . $data . '"');
            }
            $data2 = array();
            foreach ($arr[1] as $data) {
                array_push($data2, '"' . $data . '"');
            }
            $data3 = array();
            foreach ($arr[2] as $data) {
                foreach ($data as $datan) {
                    array_push($data3, '"' . $datan . '"');
                }
                array_push($data3, '\n');
            }
            array_push($data3, 'The list of questioned elements:');
            array_push($data3, '\n');

            $elems1 =  implode(',', $data1);
            $elems2 =  implode(',', $data2);
            $elems3 =  implode('\n', $data3);
            //var_dump($arr[0]);
        }
    }
    // include_once 'parser.php';
    ?>


</div>




<script type="module">
    //------------------------------------------------------------------------------------------------------------------
    // Import the modules we need for this example
    //------------------------------------------------------------------------------------------------------------------

    import {
        Viewer,
        XKTLoaderPlugin,
        NavCubePlugin,
        TreeViewPlugin
    } from "./dist/xeokit-sdk.min.es.js";

    //------------------------------------------------------------------------------------------------------------------
    // Create a Viewer, arrange the camera, tweak x-ray and highlight materials
    //------------------------------------------------------------------------------------------------------------------

    const viewer = new Viewer({
        canvasId: "my-Canvas",
        transparent: true
    });

    viewer.cameraControl.followPointer = true;

    viewer.camera.eye = [-3.933, 2.855, 27.018];
    viewer.camera.look = [4.400, 3.724, 8.899];
    viewer.camera.up = [-0.018, 0.999, 0.039];

    viewer.scene.highlightMaterial.fillAlpha = 0.3;
    viewer.scene.highlightMaterial.edgeColor = [1, 1, 0];

    // 3
    viewer.scene.xrayMaterial.fillColor = [0.0, 0.0, 1.0];
    viewer.scene.xrayMaterial.edgeColor = [0.0, 0.0, 0.0];
    viewer.scene.xrayMaterial.fillAlpha = 0.1;
    viewer.scene.xrayMaterial.edgeAlpha = 0.4;

    //------------------------------------------------------------------------------------------------------------------
    // Create a NavCube
    //------------------------------------------------------------------------------------------------------------------

    new NavCubePlugin(viewer, {
        canvasId: "my-CubeCanvas",
        visible: true,
        size: 250,
        alignment: "bottomRight",
        bottomMargin: 100,
        rightMargin: 10
    });



    //------------------------------------------------------------------------------------------------------------------
    // Load model and metadata
    //------------------------------------------------------------------------------------------------------------------



    const xktLoader = new XKTLoaderPlugin(viewer);

    const model = xktLoader.load({
        id: "myModel",
        src: "<?= './models_xkt/' . $model ?>",
        excludeTypes: [<?= 0 ?>],
        globalizeObjectIds: true, // to map GUIDs
        edges: true
    });

    const t0 = performance.now();

    document.getElementById("time").innerHTML = "Loading model...";

    model.on("loaded", function() {

        const t1 = performance.now();
        document.getElementById("time").innerHTML = "Model loaded in " + Math.floor(t1 - t0) / 1000.0 + " seconds<br>Objects: " + model.numEntities;

        //-------------------------------------------------------------------------------
        // 2. Xray and colorize objects in the third storey
        //-------------------------------------------------------------------------------



        // 2
        const ids1 = [<?= $elems1 ?>];
        viewer.scene.setObjectsColorized(ids1, [1, 0, 0]);
        const ids2 = [<?= $elems2 ?>];
        viewer.scene.setObjectsXRayed(ids2, true)
    });




    //------------------------------------------------------------------------------------------------------------------
    // Click Entities to colorize them
    //------------------------------------------------------------------------------------------------------------------

    var lastEntity = null;
    var lastColorize = null;

    viewer.cameraControl.on("picked", (pickResult) => {

        if (!pickResult.entity) {
            return;
        }

        console.log(pickResult.entity.id);

        if (!lastEntity || pickResult.entity.id !== lastEntity.id) {

            if (lastEntity) {
                lastEntity.colorize = lastColorize;
            }

            lastEntity = pickResult.entity;
            lastColorize = pickResult.entity.colorize ? pickResult.entity.colorize.slice() : null;

            pickResult.entity.colorize = [0.0, 1.0, 0.0];
        }
    });

    viewer.cameraControl.on("pickedNothing", () => {
        if (lastEntity) {
            lastEntity.colorize = lastColorize;
            lastEntity = null;
        }
    });


    // THIS IS THE PART FOR FILE DOWNLOADING //

    function download(filename, text) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
    }

    // Start file download.
    download("report.txt", '<?= $elems3, $elems1 ?>');



    // PART OF POP_UP GOOGLE MAP LOCATION
    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the button that opens the modal
    var btn = document.getElementById("myBtn");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on the button, open the modal
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
</script>


<div class="canvas">
    <canvas id="my-Canvas"></canvas>
    <canvas id="my-CubeCanvas"></canvas>
</div>
<div id="time">Loading JavaScript modules...</div>


<!-- POP UP CONTENT -->
<div id="myModal" class="modal">

    <div class="modal-content">
        <span class="close">&times;</span>
        <p style="text-align:center;"><b>Your project location is:</b></p><br>
        <div class="map">
            <iframe width="450" height="450" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="<?= $reference ?>"></iframe>
        </div>
    </div>

</div>



</body>

</html>