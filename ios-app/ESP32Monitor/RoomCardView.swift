import SwiftUI

/// 방 1개를 나타내는 행 (방 이름 + 상세 + 상태 배지).
struct RoomCardView: View {
    let room: RoomViewState

    var body: some View {
        HStack(spacing: 12) {
            // 상태 색 점
            Circle()
                .fill(room.status.color)
                .frame(width: 12, height: 12)

            VStack(alignment: .leading, spacing: 3) {
                Text(room.room)
                    .font(.headline)
                if let detail = room.detail {
                    Text(detail)
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else if room.status == .noSensor {
                    Text("센서 미설치")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            StatusBadge(status: room.status)
        }
        .padding(.vertical, 6)
    }
}

/// 상태 배지 (활동중/정지/...).
struct StatusBadge: View {
    let status: RoomStatus

    var body: some View {
        Text(status.label)
            .font(.subheadline.weight(.semibold))
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(status.color.opacity(0.18))
            .foregroundColor(status.color)
            .clipShape(Capsule())
    }
}
