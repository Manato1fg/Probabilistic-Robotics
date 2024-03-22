from simulator import agent, camera, landmark, map, robot, world

if __name__ == '__main__':
    m = map.Map()
    m.append_landmark(landmark.LandMark(2, -2, 1))
    m.append_landmark(landmark.LandMark(-1, -3, 2))
    w = world.World(30, 0.3)
    for i in range(1):
        a = agent.Agent(0.0, 10.0 / 180 * 3.14159)
        r = robot.Robot(
            robot.Pose(0, 3, 3 * 3.14159 / 2),
            agent=a,
            sensor=camera.Camera(m, phantom_prob=0.2),
            color="red",
            expected_escape_time=10.0,
            expected_stuck_time=10.0,
            expected_kidnap_time=30.0
        )
        w.append(r)

    w.append(m)
    w.draw()
