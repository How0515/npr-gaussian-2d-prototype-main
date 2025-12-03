# `brush.py` 모듈 상세 분석 보고서

이 문서는 `backend/core/brush.py` 모듈의 역할, 주요 로직, 그리고 각 클래스 및 메서드의 입출력 및 그 목적에 대해 상세히 분석합니다. 이 모듈은 3D Gaussian Splatting 기반 페인팅 시스템의 핵심 요소인 브러시(Brush)의 정의와 스트로크(Stroke)를 따라 브러시를 적용하는 로직을 구현합니다.

## 모듈의 핵심 역할

`brush.py` 모듈은 두 가지 주요 클래스 `BrushStamp`와 `StrokePainter`를 통해 브러시 기반의 페인팅 기능을 구현합니다.

1.  **`BrushStamp`**: 하나의 브러시 패턴을 구성하는 `Gaussian2D` 객체들의 집합을 정의하고 관리합니다. 브러시의 모양, 크기, 색상, 불투명도 등 런타임에 변경될 수 있는 파라미터를 효율적으로 적용하고, 주어진 위치와 방향에 브러시 패턴을 배치하는 기능을 제공합니다. 특히, 객체 생성 오버헤드를 줄이기 위해 NumPy 배열 기반의 배치(Batch) 처리 기능을 강화했습니다.
2.  **`StrokePainter`**: 사용자가 마우스 드래그 등으로 생성하는 `StrokeSpline`을 따라 `BrushStamp`를 배치하여 실제 씬(Scene)에 가우시안을 추가하는 역할을 합니다. 스트로크의 시작, 업데이트, 종료 로직을 관리하며, 비강체 변형(Non-rigid Deformation) 및 인페인팅(Inpainting)과 같은 고급 기능을 연동하여 실제 페인팅과 유사한 효과를 구현합니다.

---

## `BrushStamp` 클래스 분석

### 1. 클래스 역할

하나의 브러시 '스탬프' 또는 '패턴'을 나타냅니다. 이 클래스는 여러 개의 `Gaussian2D` 객체로 구성되며, 이 가우시안들은 서로 상대적인 위치를 유지하면서 그룹을 이룹니다. 브러시 패턴 자체는 중립적인 속성(색상, 크기)을 가지며, 실제 페인팅 시점에 동적으로 색상, 크기, 불투명도 등의 런타임 파라미터가 적용됩니다.

### 2. 주요 속성 (Attributes)

`__init__` 메서드에서 초기화됩니다.

*   `gaussians`: `List[Gaussian2D]` - 런타임 파라미터가 적용된 현재 작업 중인 가우시안 목록.
*   `base_gaussians`: `List[Gaussian2D]` - 브러시의 원본 패턴을 구성하는 불변(immutable) 가우시안 목록.
*   `center`: `np.ndarray` - `base_gaussians`의 평균 위치(중심).
*   `tangent`, `normal`, `binormal`: `np.ndarray` - 브러시의 로컬 좌표계 (tangent는 브러시의 '앞' 방향).
*   `current_color`: `np.ndarray` - 현재 브러시에 적용될 색상.
*   `current_size_multiplier`: `float` - 현재 브러시에 적용될 크기 배율.
*   `current_global_opacity`: `float` - 현재 브러시에 적용될 전체 불투명도 배율.
*   `spacing`: `float` - 스트로크를 따라 브러시 스탬프가 배치될 간격(호 길이).
*   `metadata`: `dict` - 브러시 라이브러리 저장을 위한 메타데이터.
*   `size`: `float` - 브러시 패턴의 공간적 범위(바운딩 박스 대각선 길이).

### 3. 주요 메서드 (Methods) 분석

#### `create_circular_pattern(self, ...)`
*   **역할**: 원형 브러시 패턴을 생성합니다. 지정된 개수의 가우시안을 원형으로 배치합니다.
*   **입력**: `num_gaussians`, `radius`, `gaussian_scale`, `opacity`. `color`는 하위 호환성을 위해 유지되지만 실제로는 중립적인 회색으로 패턴이 생성됩니다.
*   **로직 분석**:
    *   **로직**: `base_gaussians`를 초기화하고, `num_gaussians`만큼 반복하며 원 주위(`angle`)에 `Gaussian2D` 객체들의 `position`을 계산하여 추가합니다. 모든 `Gaussian2D`는 중립적인 회색(`0.5, 0.5, 0.5`)을 가집니다.
    *   **이유**: 브러시 패턴 자체는 색상에 독립적으로 모양만 정의하고, 실제 색상은 `apply_parameters`에서 런타임에 적용하기 위함입니다. `_update_center()`와 `_compute_size()`를 호출하여 중심과 크기를 갱신합니다.

#### `create_line_pattern(self, ...)`
*   **역할**: 선형 브러시 패턴을 생성합니다. 지정된 개수의 가우시안을 일직선으로 배치합니다.
*   **입력**: `num_gaussians`, `length`, `thickness`, `opacity`.
*   **로직 분석**:
    *   **로직**: `base_gaussians`를 초기화하고, `num_gaussians`만큼 반복하며 선형(`t`)에 따라 `Gaussian2D` 객체들의 `position`을 계산하여 추가합니다.
    *   **이유**: 원형 패턴과 유사하게 브러시의 모양을 정의하며, 색상은 런타임에 적용됩니다. `_update_center()`와 `_compute_size()`를 호출하여 중심과 크기를 갱신합니다.

#### `create_grid_pattern(self, ...)`
*   **역할**: 격자형 브러시 패턴을 생성합니다. 지정된 `grid_size`만큼 NxN 격자로 가우시안을 배치합니다.
*   **입력**: `grid_size`, `spacing`, `gaussian_scale`, `opacity`.
*   **로직 분석**:
    *   **로직**: `base_gaussians`를 초기화하고, 이중 루프를 통해 `grid_size`만큼 `x`, `y` `position`을 계산하여 `Gaussian2D` 객체들을 추가합니다.
    *   **이유**: 다양한 브러시 모양을 정의하기 위한 유연한 패턴 생성 방법입니다. `_update_center()`와 `_compute_size()`를 호출하여 중심과 크기를 갱신합니다.

#### `place_at(self, position, tangent, normal) -> List[Gaussian2D]`
*   **역할**: 하나의 브러시 스탬프를 주어진 월드 좌표계의 `position`, `tangent`(접선), `normal`(법선)에 맞춰 배치합니다. 이 함수는 스탬프를 구성하는 각 `Gaussian2D` 객체에 개별적으로 변환을 적용합니다.
*   **입력**: `position` (3D 위치), `tangent` (접선 벡터), `normal` (법선 벡터).
*   **출력**: 변환이 적용된 `Gaussian2D` 객체 리스트.
*   **로직 분석**:
    *   **로직**: 입력된 `tangent`와 `normal`로부터 `binormal`을 계산하여 월드 좌표계의 회전 프레임(`R_tgt`)을 구축합니다. 브러시의 로컬 프레임(`R_src`)과의 차이를 계산하여 회전 행렬 `R`을 얻습니다. 이 회전 행렬과 `position`을 사용하여 4x4 동차 변환 행렬 `T`를 생성합니다. 마지막으로, `self.gaussians`의 각 `Gaussian2D` 객체에 `g.transform(T)`를 적용하여 변환된 새 `Gaussian2D` 객체를 반환합니다.
    *   **이유**: 브러시 패턴이 스트로크의 특정 지점에 정확히 배치되고 방향이 맞춰지도록 합니다.

#### `place_at_batch(self, positions, tangents, normals) -> List[List[Gaussian2D]]`
*   **역할**: 여러 위치에 브러시 스탬프를 배치하는 `place_at`의 배치(Batch) 버전입니다. 여러 스탬프를 동시에 효율적으로 배치하여 성능을 향상시킵니다.
*   **입력**: `positions` (N, 3), `tangents` (N, 3), `normals` (N, 3) 형태의 NumPy 배열.
*   **출력**: N개의 리스트를 포함하는 리스트. 각 내부 리스트는 해당 위치에 배치된 `Gaussian2D` 객체들을 담습니다.
*   **로직 분석**:
    *   **로직**: `place_at`과 유사한 로직을 사용하지만, 모든 `position`, `tangent`, `normal` 쌍에 대해 한 번에 `binormal`을 계산하고 `R_batch` (N, 3, 3) 형태의 회전 행렬들을 구축합니다. 가우시안의 위치와 회전은 `np.einsum` 및 `quaternion_multiply_broadcast`와 같은 NumPy/쿼터니언 유틸리티를 사용하여 벡터화된 방식으로 변환됩니다.
    *   **이유**: Python 루프 내에서 개별 `Gaussian2D` 객체를 반복적으로 생성하고 변환하는 것보다 훨씬 빠르며, `place_at`보다 10-20배 더 빠릅니다. 최종적으로 `Gaussian2D` 객체들을 리스트 형태로 반환합니다.

#### `place_at_batch_arrays(self, positions, tangents, normals) -> dict`
*   **역할**: `place_at_batch`의 확장 버전으로, 배치된 가우시안을 `Gaussian2D` 객체 리스트 대신 NumPy 배열 딕셔너리로 반환하여 객체 생성 오버헤드를 완전히 제거합니다. `SceneData`와 같은 배열 기반 씬 관리 시스템과의 연동에 최적화되어 있습니다.
*   **입력**: `positions` (N, 3), `tangents` (N, 3), `normals` (N, 3) 형태의 NumPy 배열.
*   **출력**: `{'positions': (N, M, 3), 'rotations': (N, M, 4), ...}` 형태의 딕셔너리. (N은 스탬프 개수, M은 스탬프당 가우시안 개수).
*   **로직 분석**:
    *   **로직**: `place_at_batch`와 동일한 벡터화된 변환 로직을 사용합니다. 하지만 마지막 단계에서 `Gaussian2D` 객체를 생성하는 대신, 변환된 `positions`, `rotations`, `scales`, `colors`, `opacities` 배열을 직접 구성하여 딕셔너리로 반환합니다. `scales`, `colors`, `opacities`는 `np.broadcast_to`를 사용하여 (N, M, ...) 형태로 확장됩니다.
    *   **이유**: `Gaussian2D` 객체 생성/소멸에 드는 비용을 없애 `place_at_batch`보다 40-80배 더 빠릅니다. `SceneData` 클래스와 결합하여 사용될 때 최상의 성능을 제공합니다.

#### `apply_parameters(self, color, size_multiplier, global_opacity, spacing)`
*   **역할**: 브러시의 `base_gaussians` 패턴에 런타임 파라미터(색상, 크기, 불투명도, 간격)를 적용하여 `gaussians` (작업용 가우시안 목록)를 갱신합니다. 이 메서드는 브러시의 모양은 유지하면서 시각적 속성만 변경할 때 사용됩니다.
*   **입력**: `color`, `size_multiplier`, `global_opacity`, `spacing`. `None`이 입력되면 현재 값이 유지됩니다.
*   **로직 분석**:
    *   **로직**: `base_gaussians`를 순회하며 각 `Gaussian2D`를 복사(`g.copy()`)한 후, `current_color`, `current_size_multiplier`, `current_global_opacity` 값을 사용하여 해당 `g.color`, `g.scale`, `g.opacity`를 수정합니다. 색상 적용 시에는 패턴의 밝기 변화를 유지하기 위해 기존 색상의 휘도(luminance)를 활용합니다.
    *   **이유**: 브러시 패턴의 불변성을 유지하면서도 사용자의 입력에 따라 동적으로 브러시의 외형을 변경할 수 있도록 합니다.

#### 기타 주요 메서드
*   `_update_center()`: `base_gaussians` (또는 `gaussians`)의 평균 위치를 계산하여 `self.center`를 갱신합니다.
*   `_compute_size()`: `base_gaussians`의 바운딩 박스 대각선 길이를 계산하여 브러시의 공간적 크기 `self.size`를 갱신합니다.
*   `add_gaussian(self, gaussian: Gaussian2D)`: 브러시 패턴에 단일 `Gaussian2D`를 추가합니다. `base_gaussians`와 `gaussians`를 모두 갱신합니다.
*   `get_bounds() -> Tuple[np.ndarray, np.ndarray]`: 현재 `gaussians`의 바운딩 박스 (min_pos, max_pos)를 반환합니다.
*   `copy() -> 'BrushStamp'`: 브러시 스탬프 객체의 깊은 복사본(deep copy)을 생성합니다.
*   `__len__()`, `__repr__()`: 내장 함수 `len()`과 `print()` 사용 시 각각 가우시안 개수와 객체 표현 문자열을 반환합니다.
*   `to_dict()`, `from_dict()`: 브러시를 직렬화/역직렬화하여 저장하거나 불러올 때 사용됩니다. (`BrushSerializer`와 연동)

---

## `StrokePainter` 클래스 분석

### 1. 클래스 역할

`BrushStamp`를 사용하여 `StrokeSpline`을 따라 가우시안을 씬에 추가하는 페인팅 로직을 담당합니다. 사용자의 스트로크 입력(마우스 드래그)에 반응하여 브러시 스탬프를 적절한 위치와 방향에 배치하고, 필요에 따라 비강체 변형 및 인페인팅과 같은 후처리 작업을 수행합니다.

### 2. 주요 속성 (Attributes)

`__init__` 메서드에서 초기화됩니다.

*   `brush`: `BrushStamp` - 현재 페인팅에 사용될 브러시 스탬프 객체.
*   `scene`: `SceneData` 또는 `List[Gaussian2D]` - 가우시안이 추가될 씬 데이터 구조. `SceneData` 사용 시 `use_arrays=True`.
*   `use_arrays`: `bool` - 현재 씬 관리가 NumPy 배열 기반(`SceneData`)인지 여부.
*   `current_stroke`: `Optional[StrokeSpline]` - 현재 진행 중인 스트로크의 스플라인 객체.
*   `placed_stamps`: `List[Tuple[List[Gaussian2D] / dict, float]]` - 스트로크를 따라 배치된 개별 스탬프(가우시안 리스트 또는 배열 딕셔너리)와 해당 스탬프가 배치된 스플라인의 호 길이(arc length)를 저장합니다.
*   `stamp_placements`: `List[Tuple[np.ndarray, np.ndarray, np.ndarray, float]]` - 변형(deformation)을 위해 브러시가 배치된 위치, 접선, 법선, 호 길이를 저장합니다.
*   `last_stamp_arc_length`: `float` - 마지막으로 스탬프가 배치된 스플라인의 호 길이.
*   `current_stroke_start_index`: `int` - 현재 스트로크가 씬에 추가되기 시작한 인덱스 (씬에서 임시로 제거/수정할 때 사용).
*   `enable_deformation_for_current_stroke`: `bool` - 현재 스트로크에 변형을 적용할지 여부.

### 3. 주요 메서드 (Methods) 분석

#### `start_stroke(self, position, normal, enable_deformation)`
*   **역할**: 새로운 페인팅 스트로크를 시작합니다.
*   **입력**: `position` (3D 시작 위치), `normal` (표면 법선), `enable_deformation` (이 스트로크에 변형을 적용할지 여부).
*   **로직 분석**:
    *   **로직**: `StrokeSpline` 객체를 새로 생성하고, 첫 번째 점(`position`, `normal`)을 추가합니다. `placed_stamps`, `stamp_placements` 등 스트로크 관련 내부 상태를 초기화하고, 씬에 현재 스트로크가 추가되기 시작할 인덱스를 기록합니다. `enable_deformation_for_current_stroke` 플래그를 설정합니다.
    *   **이유**: 새로운 페인팅 동작을 시작하고, 스트로크를 따라 브러시를 배치하기 위한 준비를 합니다.

#### `update_stroke(self, position, normal)`
*   **역할**: 현재 진행 중인 스트로크에 새로운 점을 추가하고, 그에 따라 브러시 스탬프를 배치합니다.
*   **입력**: `position` (새로운 3D 위치), `normal` (표면 법선).
*   **로직 분석**:
    *   **로직**: `current_stroke`에 새로운 점을 추가합니다. 점이 성공적으로 추가되면 (`added`가 True), `_place_new_stamps()`를 호출하여 스플라인의 새로운 구간에 브러시 스탬프를 배치합니다.
    *   **이유**: 사용자의 마우스 드래그 동작에 실시간으로 반응하여 스트로크를 연장하고 브러시를 그려나가게 합니다.

#### `_place_new_stamps(self)`
*   **역할**: `last_stamp_arc_length` 이후부터 스플라인의 현재 끝까지 새로운 브러시 스탬프를 배치합니다. 효율성을 위해 배치(Batch) 처리 방식을 사용합니다.
*   **로직 분석**:
    *   **로직**: `current_stroke.total_arc_length`와 `self.brush.spacing`을 이용하여 새로 배치될 스탬프들의 호 길이(`arc_lengths`)를 계산합니다. 각 호 길이에 해당하는 `position`, `tangent`, `normal`을 스플라인에서 추출합니다.
    *   **변형(Deformation) 활성화 시**: 임시로 강체(rigid) 스탬프를 씬에 배치하여 즉각적인 시각화를 제공하고, 실제 변형을 위한 `stamp_placements` 정보를 저장합니다.
    *   **변형 비활성화 시**: `brush.place_at_batch_arrays` (또는 레거시 모드에서는 `brush.place_at_batch`)를 사용하여 모든 스탬프를 배치하고 씬에 추가합니다.
    *   **이유**: 브러시 간격에 맞춰 스탬프를 연속적으로 배치하며, 성능을 위해 NumPy 기반의 벡터화된 배치 기능을 최대한 활용합니다.

#### `finish_stroke(self, enable_deformation, enable_inpainting, ...)`
*   **역할**: 현재 스트로크를 완료하고, 최종적으로 비강체 변형 및/또는 인페인팅을 적용하여 씬에 가우시안을 추가합니다.
*   **입력**: `enable_deformation` (변형 적용 여부), `enable_inpainting` (인페인팅 적용 여부) 및 인페인팅 관련 파라미터들.
*   **로직 분석**:
    *   **변형 적용 (`enable_deformation`이 True인 경우)**: 임시로 씬에 추가했던 강체 스탬프를 삭제합니다 (`del self.scene[self.current_stroke_start_index:]`). `stamp_placements`에 저장된 정보를 사용하여 `deformation_gpu.deform_all_stamps_batch_gpu` (GPU 가속) 또는 CPU 기반의 `deformation.deform_stamp_along_spline` 함수를 호출하여 각 스탬프에 비강체 변형을 적용합니다.
    *   **인페인팅 적용 (`enable_inpainting`이 True인 경우)**: 변형된 스탬프(또는 변형이 없는 경우 `placed_stamps`의 원본 스탬프)들에 대해 `inpainting.blend_overlapping_stamps_auto` 함수를 호출하여 겹치는 부분의 불투명도를 조정하거나 색상을 블렌딩합니다.
    *   **최종 추가**: 변형 및/또는 인페인팅이 완료된 스탬프들을 `self.scene.extend`를 통해 씬에 추가합니다. 모든 스트로크 관련 내부 상태를 초기화합니다.
    *   **이유**: 사용자의 페인팅 의도를 더 잘 반영하고, 브러시 스트로크의 시각적 품질을 향상시키기 위한 후처리 단계입니다. GPU 가속을 통해 복잡한 변형 계산도 빠르게 수행할 수 있습니다.

#### 기타 메서드
*   `get_stroke_gaussians() -> List[Gaussian2D]`: 현재 스트로크에 의해 배치된 모든 `Gaussian2D` 객체들을 리스트로 반환합니다.
*   `clear_scene()`: 현재 씬의 모든 가우시안을 삭제합니다.

---
