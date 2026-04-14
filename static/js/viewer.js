/**
 * Babylon.js 3Dビューアの初期化と管理
 * USDシーンのリアルタイムレンダリング
 */

class RobotViewer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.engine = null;
        this.scene = null;
        this.camera = null;
        this.meshes = {};
        this.materials = {};
        this.gridEnabled = true;
        this.shadowGenerator = null;
        this.robotMeshCache = {};
        
        this.init();
    }

    init() {
        // Babylon.js エンジンとシーンの初期化（アンチエイリアス有効）
        this.engine = new BABYLON.Engine(this.canvas, true, {
            preserveDrawingBuffer: true,
            stencil: true
        });
        
        this.scene = new BABYLON.Scene(this.engine);
        this.scene.clearColor = new BABYLON.Color4(0.05, 0.05, 0.1, 1.0);
        
        // 環境テクスチャでよりリアルな反射を追加
        this.scene.environmentIntensity = 0.5;

        // カメラの設定（改善されたコントロール）
        this.camera = new BABYLON.ArcRotateCamera(
            "camera",
            -Math.PI / 4,        // alpha (水平角度)
            Math.PI / 3,         // beta (垂直角度)
            3.0,                 // radius (距離)
            new BABYLON.Vector3(0, 0.3, 0),  // target (注視点)
            this.scene
        );
        this.camera.attachControl(this.canvas, true);
        this.camera.lowerRadiusLimit = 0.5;
        this.camera.upperRadiusLimit = 15;
        this.camera.wheelPrecision = 30;
        this.camera.panningSensibility = 50;
        this.camera.pinchPrecision = 50;

        // ライティングシステムの強化
        this.setupLighting();

        // グリッドと環境の作成
        this.createGrid();
        this.createAxes();
        this.createEnvironment();
        
        // テストメッシュを追加（デバッグ用）
        this.createTestRobot();

        // レンダリングループ
        this.engine.runRenderLoop(() => {
            this.scene.render();
            this.updateFPS();
        });

        // ウィンドウリサイズ対応
        window.addEventListener('resize', () => {
            this.engine.resize();
        });
        
        console.log('Babylon.js viewer initialized');
    }
    
    setupLighting() {
        // 環境光（全体の明るさ）
        const hemisphericLight = new BABYLON.HemisphericLight(
            "hemisphericLight",
            new BABYLON.Vector3(0, 1, 0),
            this.scene
        );
        hemisphericLight.intensity = 0.6;
        hemisphericLight.groundColor = new BABYLON.Color3(0.1, 0.1, 0.2);

        // メインライト（シャドウあり）
        const directionalLight = new BABYLON.DirectionalLight(
            "directionalLight",
            new BABYLON.Vector3(-0.5, -1, -0.5),
            this.scene
        );
        directionalLight.position = new BABYLON.Vector3(2, 3, 2);
        directionalLight.intensity = 0.8;
        
        // シャドウジェネレーター
        this.shadowGenerator = new BABYLON.ShadowGenerator(1024, directionalLight);
        this.shadowGenerator.useBlurExponentialShadowMap = true;
        this.shadowGenerator.blurScale = 2;
        this.shadowGenerator.darkness = 0.4;

        // フィルライト（柔らかい補助光）
        const fillLight = new BABYLON.PointLight(
            "fillLight",
            new BABYLON.Vector3(-1, 1, 1),
            this.scene
        );
        fillLight.intensity = 0.3;
        fillLight.diffuse = new BABYLON.Color3(0.8, 0.9, 1.0);
    }
    
    createEnvironment() {
        // 背景のスカイボックス風の色
        this.scene.clearColor = new BABYLON.Color4(0.02, 0.02, 0.05, 1.0);
        
        // フォグ効果（オプション）
        // this.scene.fogMode = BABYLON.Scene.FOGMODE_LINEAR;
        // this.scene.fogStart = 5.0;
        // this.scene.fogEnd = 20.0;
        // this.scene.fogColor = new BABYLON.Color3(0.05, 0.05, 0.1);
    }


    createGrid() {
        // グリッド平面（より詳細）
        const ground = BABYLON.MeshBuilder.CreateGround(
            "ground",
            { width: 5, height: 5, subdivisions: 50 },
            this.scene
        );
        
        const groundMaterial = new BABYLON.GridMaterial("groundMat", this.scene);
        groundMaterial.majorUnitFrequency = 5;
        groundMaterial.minorUnitVisibility = 0.3;
        groundMaterial.gridRatio = 0.1;
        groundMaterial.backFaceCulling = false;
        groundMaterial.mainColor = new BABYLON.Color3(0.1, 0.1, 0.2);
        groundMaterial.lineColor = new BABYLON.Color3(0.3, 0.4, 0.6);
        groundMaterial.opacity = 0.8;
        
        ground.material = groundMaterial;
        ground.receiveShadows = true;
        
        this.meshes.ground = ground;
    }

    createAxes() {
        const axisSize = 1.0;
        const axisThickness = 3;
        
        // X軸 (赤)
        const axisX = BABYLON.MeshBuilder.CreateLines("axisX", {
            points: [
                BABYLON.Vector3.Zero(),
                new BABYLON.Vector3(axisSize, 0, 0)
            ]
        }, this.scene);
        axisX.color = new BABYLON.Color3(1, 0.2, 0.2);
        axisX.isPickable = false;
        
        // X軸ラベル
        const xLabel = BABYLON.MeshBuilder.CreatePlane("xLabel", {size: 0.1}, this.scene);
        xLabel.position = new BABYLON.Vector3(axisSize + 0.1, 0, 0);
        const xMat = new BABYLON.StandardMaterial("xMat", this.scene);
        xMat.diffuseColor = new BABYLON.Color3(1, 0.2, 0.2);
        xMat.emissiveColor = new BABYLON.Color3(0.3, 0, 0);
        xLabel.material = xMat;

        // Y軸 (緑)
        const axisY = BABYLON.MeshBuilder.CreateLines("axisY", {
            points: [
                BABYLON.Vector3.Zero(),
                new BABYLON.Vector3(0, axisSize, 0)
            ]
        }, this.scene);
        axisY.color = new BABYLON.Color3(0.2, 1, 0.2);
        axisY.isPickable = false;

        // Z軸 (青)
        const axisZ = BABYLON.MeshBuilder.CreateLines("axisZ", {
            points: [
                BABYLON.Vector3.Zero(),
                new BABYLON.Vector3(0, 0, axisSize)
            ]
        }, this.scene);
        axisZ.color = new BABYLON.Color3(0.2, 0.4, 1);
        axisZ.isPickable = false;
    }
    
    /**
     * テスト用のシンプルなロボットを作成
     */
    createTestRobot() {
        console.log('Creating test robot...');
        
        // ベース
        const base = BABYLON.MeshBuilder.CreateCylinder("testBase", {
            height: 0.1,
            diameter: 0.3
        }, this.scene);
        base.position.y = 0.05;
        
        const baseMat = new BABYLON.StandardMaterial("baseMat", this.scene);
        baseMat.diffuseColor = new BABYLON.Color3(0.3, 0.3, 0.3);
        baseMat.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2);
        base.material = baseMat;
        
        // リンク1
        const link1 = BABYLON.MeshBuilder.CreateCylinder("testLink1", {
            height: 0.3,
            diameter: 0.06
        }, this.scene);
        link1.position = new BABYLON.Vector3(0, 0.25, 0);
        link1.rotation.z = Math.PI / 2;
        
        const link1Mat = new BABYLON.StandardMaterial("link1Mat", this.scene);
        link1Mat.diffuseColor = new BABYLON.Color3(0.2, 0.5, 0.8);
        link1Mat.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        link1.material = link1Mat;
        
        // 関節マーカー
        const joint1 = BABYLON.MeshBuilder.CreateSphere("testJoint1", {
            diameter: 0.08
        }, this.scene);
        joint1.position = new BABYLON.Vector3(0, 0.1, 0);
        
        const jointMat = new BABYLON.StandardMaterial("jointMat", this.scene);
        jointMat.diffuseColor = new BABYLON.Color3(1.0, 0.5, 0.0);
        jointMat.emissiveColor = new BABYLON.Color3(0.2, 0.1, 0.0);
        joint1.material = jointMat;
        
        // シャドウを追加
        if (this.shadowGenerator) {
            this.shadowGenerator.addShadowCaster(base);
            this.shadowGenerator.addShadowCaster(link1);
            this.shadowGenerator.addShadowCaster(joint1);
        }
        
        base.receiveShadows = true;
        link1.receiveShadows = true;
        joint1.receiveShadows = true;
        
        this.meshes.testBase = base;
        this.meshes.testLink1 = link1;
        this.meshes.testJoint1 = joint1;
        
        console.log('Test robot created');
    }


    /**
     * USDシーンデータからBabylon.jsシーンを更新
     * メッシュを効率的に再利用して更新
     */
    updateScene(sceneData) {
        console.log('updateScene called with:', sceneData);
        
        if (!sceneData || !sceneData.meshes) {
            console.warn('Invalid scene data received');
            return;
        }

        console.log(`Processing ${sceneData.meshes.length} meshes`);
        const newMeshKeys = new Set();

        // 各メッシュデータを処理
        sceneData.meshes.forEach((meshData, index) => {
            const meshKey = `robot_${meshData.name}_${index}`;
            newMeshKeys.add(meshKey);
            
            console.log(`Processing mesh ${index}: ${meshData.name}, type: ${meshData.type}`);

            // 既存のメッシュがあれば更新、なければ作成
            if (this.robotMeshCache[meshKey]) {
                this.updateMesh(this.robotMeshCache[meshKey], meshData);
            } else {
                const mesh = this.createMesh(meshData);
                if (mesh) {
                    this.robotMeshCache[meshKey] = mesh;
                    this.meshes[meshKey] = mesh;
                    console.log(`Created mesh: ${meshKey}`);
                } else {
                    console.error(`Failed to create mesh: ${meshKey}`);
                }
            }
        });

        // 使用されていないメッシュを削除
        Object.keys(this.robotMeshCache).forEach(key => {
            if (!newMeshKeys.has(key)) {
                this.robotMeshCache[key].dispose();
                delete this.robotMeshCache[key];
                delete this.meshes[key];
            }
        });
    }

    /**
     * 新しいメッシュを作成
     */
    createMesh(meshData) {
        let mesh;

        switch (meshData.type) {
            case 'cylinder':
                mesh = BABYLON.MeshBuilder.CreateCylinder(
                    meshData.name,
                    {
                        height: meshData.height,
                        diameter: meshData.radius * 2,
                        tessellation: 32
                    },
                    this.scene
                );
                break;

            case 'sphere':
                mesh = BABYLON.MeshBuilder.CreateSphere(
                    meshData.name,
                    {
                        diameter: meshData.radius * 2,
                        segments: 32
                    },
                    this.scene
                );
                break;

            case 'capsule':
                // カプセルを円柱 + 2つの半球で構成
                mesh = this.createCapsuleMesh(meshData);
                break;

            case 'box':
                mesh = BABYLON.MeshBuilder.CreateBox(
                    meshData.name,
                    { size: meshData.size || 0.1 },
                    this.scene
                );
                break;

            default:
                console.warn(`Unknown mesh type: ${meshData.type}`);
                return null;
        }

        if (!mesh) return null;

        // マテリアルを作成して適用
        this.applyMaterial(mesh, meshData);

        // 位置と回転を設定
        this.updateMeshTransform(mesh, meshData);

        // シャドウを有効化（メッシュの場合のみ）
        if (this.shadowGenerator && mesh instanceof BABYLON.Mesh) {
            this.shadowGenerator.addShadowCaster(mesh);
            mesh.receiveShadows = true;
        }

        return mesh;
    }

    /**
     * カプセルメッシュを作成（単一メッシュとしてマージ）
     */
    createCapsuleMesh(meshData) {
        const capsuleHeight = meshData.height || 0.1;
        const capsuleRadius = meshData.radius || 0.05;
        
        // 中央の円柱
        const cylinder = BABYLON.MeshBuilder.CreateCylinder(
            meshData.name + "_body",
            {
                height: capsuleHeight,
                diameter: capsuleRadius * 2,
                tessellation: 24
            },
            this.scene
        );
        cylinder.rotation.z = Math.PI / 2; // X軸方向に
        
        // 上部の半球
        const sphere1 = BABYLON.MeshBuilder.CreateSphere(
            meshData.name + "_cap1",
            { diameter: capsuleRadius * 2, segments: 16 },
            this.scene
        );
        sphere1.position.x = capsuleHeight / 2;
        
        // 下部の半球
        const sphere2 = BABYLON.MeshBuilder.CreateSphere(
            meshData.name + "_cap2",
            { diameter: capsuleRadius * 2, segments: 16 },
            this.scene
        );
        sphere2.position.x = -capsuleHeight / 2;
        
        // メッシュをマージ
        const capsule = BABYLON.Mesh.MergeMeshes(
            [cylinder, sphere1, sphere2],
            true,  // disposeSource
            true,  // allow32BitsIndices
            undefined,
            false, // multiMultiMaterial
            true   // preserveScaling
        );
        
        if (capsule) {
            capsule.name = meshData.name;
            return capsule;
        } else {
            console.warn(`Failed to merge capsule mesh: ${meshData.name}`);
            // フォールバック: シンプルな円柱を返す
            const fallback = BABYLON.MeshBuilder.CreateCylinder(
                meshData.name,
                {
                    height: capsuleHeight,
                    diameter: capsuleRadius * 2,
                    tessellation: 24
                },
                this.scene
            );
            fallback.rotation.z = Math.PI / 2;
            return fallback;
        }
    }

    /**
     * マテリアルを作成
     */
    createMaterial(meshData) {
        const materialName = meshData.name + "_mat";
        
        const material = new BABYLON.PBRMetallicRoughnessMaterial(
            materialName,
            this.scene
        );
        
        // ベースカラー
        material.baseColor = new BABYLON.Color3(
            meshData.color[0],
            meshData.color[1],
            meshData.color[2]
        );
        
        // メタリック・ラフネス
        material.metallic = 0.3;
        material.roughness = 0.6;
        
        // 環境反射
        material.environmentIntensity = 0.4;
        
        return material;
    }

    /**
     * メッシュにマテリアルを適用
     */
    applyMaterial(mesh, meshData) {
        const material = this.createMaterial(meshData);
        mesh.material = material;
    }

    /**
     * メッシュのトランスフォームを更新
     */
    updateMeshTransform(mesh, meshData) {
        if (!mesh) return;
        
        // 位置
        if (meshData.position && Array.isArray(meshData.position)) {
            mesh.position.set(
                meshData.position[0],
                meshData.position[1],
                meshData.position[2]
            );
        }

        // 回転
        if (meshData.rotation && Array.isArray(meshData.rotation)) {
            mesh.rotation.set(
                meshData.rotation[0],
                meshData.rotation[1],
                meshData.rotation[2]
            );
        }
    }

    /**
     * 既存のメッシュを更新（位置と回転のみ）
     */
    updateMesh(mesh, meshData) {
        this.updateMeshTransform(mesh, meshData);
    }
    
    /**
     * USDシーンをロードして表示（モデル切り替え時に使用）
     */
    loadUSDScene(sceneData) {
        console.log('loadUSDScene called with:', sceneData);
        
        // テストロボットを削除
        if (this.meshes.testBase) {
            this.meshes.testBase.dispose();
            delete this.meshes.testBase;
        }
        if (this.meshes.testLink1) {
            this.meshes.testLink1.dispose();
            delete this.meshes.testLink1;
        }
        if (this.meshes.testJoint1) {
            this.meshes.testJoint1.dispose();
            delete this.meshes.testJoint1;
        }
        
        // 既存のロボットメッシュをクリア
        Object.values(this.robotMeshCache).forEach(mesh => {
            if (mesh && mesh.dispose) mesh.dispose();
        });
        this.robotMeshCache = {};
        
        // 新しいシーンをロード
        this.updateScene(sceneData);
        
        // カメラを調整
        this.resetView();
    }


    resetView() {
        this.camera.alpha = -Math.PI / 4;
        this.camera.beta = Math.PI / 3;
        this.camera.radius = 2.5;
        this.camera.target = new BABYLON.Vector3(0.3, 0, 0.4);
    }

    toggleGrid() {
        this.gridEnabled = !this.gridEnabled;
        if (this.meshes.ground) {
            this.meshes.ground.setEnabled(this.gridEnabled);
        }
    }

    updateFPS() {
        const fpsCounter = document.getElementById('fpsCounter');
        if (fpsCounter) {
            const fps = this.engine.getFps().toFixed(0);
            const meshCount = Object.keys(this.meshes).length;
            const robotMeshCount = Object.keys(this.robotMeshCache).length;
            fpsCounter.textContent = `FPS: ${fps} | Meshes: ${meshCount} | Robot: ${robotMeshCount}`;
        }
    }

    dispose() {
        // 全メッシュを削除
        Object.values(this.meshes).forEach(mesh => {
            if (mesh && typeof mesh.dispose === 'function') {
                mesh.dispose();
            }
        });
        Object.values(this.robotMeshCache).forEach(mesh => {
            if (mesh && typeof mesh.dispose === 'function') {
                mesh.dispose();
            }
        });
        
        // シーンとエンジンを削除
        if (this.scene) this.scene.dispose();
        if (this.engine) this.engine.dispose();
    }
}

// グローバルインスタンス
let viewer = null;

// ビューアの初期化
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Robot Viewer...');
    viewer = new RobotViewer('renderCanvas');
    window.viewer = viewer;
    window.robotViewer = viewer;  // model_selector.js用
    
    // ビューリセットボタン
    const resetViewBtn = document.getElementById('resetViewBtn');
    if (resetViewBtn) {
        resetViewBtn.addEventListener('click', () => {
            viewer.resetView();
        });
    }
    
    // グリッド切替ボタン
    const toggleGridBtn = document.getElementById('toggleGridBtn');
    if (toggleGridBtn) {
        toggleGridBtn.addEventListener('click', () => {
            viewer.toggleGrid();
        });
    }
});
