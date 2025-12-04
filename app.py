#!/usr/bin/env python3
"""
Unified Flask server for Computer Vision Assignments
Serves static files and provides backend API endpoints
"""

import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
import json
import base64
from io import BytesIO
from PIL import Image

# Assignment 7 backend functions (copied to avoid import issues)
calibration_storage = {}

def create_object_points(pattern_size, square_size):
    """Create 3D object points for chessboard"""
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size
    return objp

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Get port from environment variable (Railway sets this)
PORT = int(os.environ.get('PORT', 5000))

# ========== Static File Serving ==========

@app.route('/')
def index():
    """Serve main index page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from root and assignments folders"""
    # Security: prevent directory traversal
    if '..' in path or path.startswith('/'):
        return "Forbidden", 403
    
    # URL decode the path (handles spaces like "Assignment 1")
    from urllib.parse import unquote
    decoded_path = unquote(path)
    
    # Try to serve from root first
    if os.path.exists(decoded_path):
        return send_from_directory('.', decoded_path)
    
    # Try assignments folder
    assignments_path = os.path.join('assignments', decoded_path)
    if os.path.exists(assignments_path):
        return send_from_directory('assignments', decoded_path)
    
    # Try nested paths in assignments
    parts = decoded_path.split('/')
    if len(parts) >= 2:
        nested_path = os.path.join('assignments', '/'.join(parts))
        if os.path.exists(nested_path):
            return send_from_directory('assignments', '/'.join(parts))
    
    return "Not Found", 404

# ========== Assignment 7 Backend API ==========

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'calibrations': len(calibration_storage),
        'service': 'Computer Vision Assignments'
    })

@app.route('/api/calibrate', methods=['POST'])
def calibrate_stereo():
    """Perform stereo calibration from chessboard images"""
    try:
        data = request.json
        calibration_id = data.get('id', 'default')
        pattern_size = tuple(data['pattern_size'])
        square_size = float(data['square_size'])
        image_pairs = data['image_pairs']
        
        objpoints = []
        imgpoints_left = []
        imgpoints_right = []
        
        objp = create_object_points(pattern_size, square_size)
        
        for pair in image_pairs:
            left_data = base64.b64decode(pair['left'].split(',')[1])
            right_data = base64.b64decode(pair['right'].split(',')[1])
            
            left_img = np.array(Image.open(BytesIO(left_data)))
            right_img = np.array(Image.open(BytesIO(right_data)))
            
            if len(left_img.shape) == 3:
                left_gray = cv2.cvtColor(left_img, cv2.COLOR_RGB2GRAY)
                right_gray = cv2.cvtColor(right_img, cv2.COLOR_RGB2GRAY)
            else:
                left_gray = left_img
                right_gray = right_img
            
            ret_left, corners_left = cv2.findChessboardCorners(
                left_gray, pattern_size, None
            )
            ret_right, corners_right = cv2.findChessboardCorners(
                right_gray, pattern_size, None
            )
            
            if ret_left and ret_right:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners_left = cv2.cornerSubPix(
                    left_gray, corners_left, (11, 11), (-1, -1), criteria
                )
                corners_right = cv2.cornerSubPix(
                    right_gray, corners_right, (11, 11), (-1, -1), criteria
                )
                
                objpoints.append(objp)
                imgpoints_left.append(corners_left)
                imgpoints_right.append(corners_right)
        
        if len(objpoints) < 3:
            return jsonify({
                'success': False,
                'error': f'Need at least 3 valid pairs. Found: {len(objpoints)}'
            }), 400
        
        img_shape = left_gray.shape[::-1]
        
        ret, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = \
            cv2.stereoCalibrate(
                objpoints, imgpoints_left, imgpoints_right,
                None, None, None, None,
                img_shape,
                flags=cv2.CALIB_FIX_ASPECT_RATIO,
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
            )
        
        baseline = np.linalg.norm(T)
        
        calibration_storage[calibration_id] = {
            'cameraMatrix1': cameraMatrix1.tolist(),
            'cameraMatrix2': cameraMatrix2.tolist(),
            'distCoeffs1': distCoeffs1.tolist(),
            'distCoeffs2': distCoeffs2.tolist(),
            'R': R.tolist(),
            'T': T.tolist(),
            'E': E.tolist(),
            'F': F.tolist(),
            'image_size': img_shape,
            'baseline': float(baseline)
        }
        
        return jsonify({
            'success': True,
            'baseline': float(baseline),
            'reprojection_error': float(ret),
            'pairs_used': len(objpoints)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/triangulate', methods=['POST'])
def triangulate_points():
    """Triangulate 3D points from stereo correspondences"""
    try:
        data = request.json
        calibration_id = data.get('id', 'default')
        left_points = np.array(data['left_points'], dtype=np.float32)
        right_points = np.array(data['right_points'], dtype=np.float32)
        
        if calibration_id not in calibration_storage:
            return jsonify({
                'success': False,
                'error': 'Calibration not found. Please calibrate first.'
            }), 400
        
        calib = calibration_storage[calibration_id]
        
        cameraMatrix1 = np.array(calib['cameraMatrix1'])
        cameraMatrix2 = np.array(calib['cameraMatrix2'])
        distCoeffs1 = np.array(calib['distCoeffs1'])
        distCoeffs2 = np.array(calib['distCoeffs2'])
        R = np.array(calib['R'])
        T = np.array(calib['T'])
        
        left_undistorted = cv2.undistortPoints(
            left_points.reshape(-1, 1, 2),
            cameraMatrix1, distCoeffs1, P=cameraMatrix1
        )
        right_undistorted = cv2.undistortPoints(
            right_points.reshape(-1, 1, 2),
            cameraMatrix2, distCoeffs2, P=cameraMatrix2
        )
        
        R1 = np.eye(3)
        T1 = np.zeros((3, 1))
        P1 = cameraMatrix1 @ np.hstack([R1, T1])
        
        R2 = R
        T2 = T.reshape(3, 1)
        P2 = cameraMatrix2 @ np.hstack([R2, T2])
        
        points_4d = cv2.triangulatePoints(P1, P2, 
                                         left_undistorted.reshape(-1, 2).T,
                                         right_undistorted.reshape(-1, 2).T)
        
        points_3d = points_4d[:3] / points_4d[3]
        points_3d = points_3d.T
        
        distances = np.linalg.norm(points_3d, axis=1)
        avg_distance = float(np.mean(distances))
        min_distance = float(np.min(distances))
        max_distance = float(np.max(distances))
        
        return jsonify({
            'success': True,
            'points_3d': points_3d.tolist(),
            'avg_distance': avg_distance,
            'min_distance': min_distance,
            'max_distance': max_distance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/measure_size', methods=['POST'])
def measure_object_size():
    """Measure object size from 3D points"""
    try:
        data = request.json
        points_3d = np.array(data['points_3d'])
        shape = data.get('shape', 'rectangular')
        units = data.get('units', 'mm')
        
        unit_scale = {'mm': 1.0, 'cm': 0.1, 'in': 0.0393701}[units]
        result = {}
        
        if shape == 'rectangular':
            if len(points_3d) >= 2:
                width = np.linalg.norm(points_3d[1] - points_3d[0])
                result['width'] = float(width * unit_scale)
                
                if len(points_3d) >= 4:
                    length = np.linalg.norm(points_3d[2] - points_3d[0])
                    result['length'] = float(length * unit_scale)
                    result['size'] = f"{result['width']:.2f} × {result['length']:.2f} {units}"
                else:
                    result['size'] = f"Width: {result['width']:.2f} {units}"
            else:
                return jsonify({'success': False, 'error': 'Need at least 2 points'}), 400
        else:
            return jsonify({'success': False, 'error': f'Unknown shape: {shape}'}), 400
        
        avg_z = float(np.mean(points_3d[:, 2]))
        result['avg_distance_z'] = float(avg_z * unit_scale)
        
        return jsonify({'success': True, **result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== Assignment 4 Backend API ==========

@app.route('/api/stitch_panorama', methods=['POST'])
def stitch_panorama():
    """Stitch multiple images into a panorama"""
    try:
        if 'images' not in request.files:
            return jsonify({'success': False, 'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        if len(files) < 2:
            return jsonify({'success': False, 'error': 'Need at least 2 images to stitch'}), 400
        
        # Load images
        images = []
        for file in files:
            if file.filename == '':
                continue
            img_bytes = file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return jsonify({'success': False, 'error': f'Failed to decode image: {file.filename}'}), 400
            
            # Resize if too large (max width 1800px)
            if img.shape[1] > 1800:
                scale = 1800 / img.shape[1]
                new_size = (1800, int(img.shape[0] * scale))
                img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
            
            images.append(img)
        
        if len(images) < 2:
            return jsonify({'success': False, 'error': 'Need at least 2 valid images'}), 400
        
        # Create stitcher
        mode = cv2.Stitcher_PANORAMA
        if hasattr(cv2, "Stitcher_create"):
            stitcher = cv2.Stitcher_create(mode)
        elif hasattr(cv2, "createStitcher"):
            stitcher = cv2.createStitcher(mode)
        else:
            return jsonify({'success': False, 'error': 'OpenCV Stitcher API not available'}), 500
        
        # Stitch images
        status, panorama = stitcher.stitch(images)
        
        if status != cv2.Stitcher_OK:
            error_messages = {
                cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images (at least 2)",
                cv2.Stitcher_ERR_HOMOGESTY_EST_FAIL: "Homography estimation failed - images may not have enough overlap",
                cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameters adjustment failed",
                cv2.Stitcher_ERR_MATCH_CONFIDENCE_FAIL: "Matching confidence too low - images may not overlap enough"
            }
            error_msg = error_messages.get(status, f"Stitching failed with status code {status}")
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Convert to base64
        success, buffer = cv2.imencode('.jpg', panorama, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not success:
            return jsonify({'success': False, 'error': 'Failed to encode panorama'}), 500
        
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'panorama': f'data:image/jpeg;base64,{img_base64}',
            'width': panorama.shape[1],
            'height': panorama.shape[0]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/detect_chessboard', methods=['POST'])
def detect_chessboard():
    """Detect chessboard corners in stereo image pair"""
    try:
        data = request.json
        left_data = base64.b64decode(data['left_image'].split(',')[1])
        right_data = base64.b64decode(data['right_image'].split(',')[1])
        pattern_size = tuple(data['pattern_size'])
        
        left_img = np.array(Image.open(BytesIO(left_data)))
        right_img = np.array(Image.open(BytesIO(right_data)))
        
        max_dimension = 1920
        h, w = left_img.shape[:2]
        if max(h, w) > max_dimension:
            scale = max_dimension / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            left_img = cv2.resize(left_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            right_img = cv2.resize(right_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        if len(left_img.shape) == 3:
            left_gray = cv2.cvtColor(left_img, cv2.COLOR_RGB2GRAY)
            right_gray = cv2.cvtColor(right_img, cv2.COLOR_RGB2GRAY)
        else:
            left_gray = left_img
            right_gray = right_img
        
        ret_left, corners_left = cv2.findChessboardCorners(
            left_gray, pattern_size, None
        )
        ret_right, corners_right = cv2.findChessboardCorners(
            right_gray, pattern_size, None
        )
        
        if not ret_left or not ret_right:
            return jsonify({
                'success': False,
                'error': f'Chessboard not found. Left: {ret_left}, Right: {ret_right}'
            }), 400
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_left = cv2.cornerSubPix(
            left_gray, corners_left, (11, 11), (-1, -1), criteria
        )
        corners_right = cv2.cornerSubPix(
            right_gray, corners_right, (11, 11), (-1, -1), criteria
        )
        
        return jsonify({
            'success': True,
            'left_corners': corners_left.reshape(-1, 2).tolist(),
            'right_corners': corners_right.reshape(-1, 2).tolist()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Computer Vision Assignments - Unified Server")
    print("=" * 60)
    print(f"Server starting on port {PORT}")
    print(f"Main page: http://localhost:{PORT}/")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=False)

