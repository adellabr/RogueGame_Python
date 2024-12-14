import unittest

from src.Business_Logic.model import Type_Monster, Settings
from ..Business_Logic import model


class TestMathFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test1(self):
        position = model.Position(0, 0)
        A = model.Character(position)
        self.assertEqual(A.max_health, model.Settings.MAX_HEALTH)
        self.assertEqual(A.health, model.Settings.MIDDLE_CHARACTERISTIC)
        self.assertEqual(A.power, model.Settings.MIDDLE_CHARACTERISTIC)
        self.assertEqual(A.dexterity, model.Settings.MIDDLE_CHARACTERISTIC)

    def test2(self):
        position_monster = model.Position(6, 3)
        A = model.Monster(Type_Monster.GHOST, position_monster)
        self.assertEqual(A.power, model.Settings.LOW_CHARACTERISTIC)
        self.assertEqual(A.health, model.Settings.LOW_CHARACTERISTIC)
        self.assertEqual(A.hostility, model.Settings.LOW_CHARACTERISTIC)
        self.assertEqual(A.dexterity, model.Settings.HIGH_CHARACTERISTIC)

    def test3(self):
        position = model.Position(0, 0)
        A = model.Character(position)
        new_object = model.Object(
            model.Type_Object.SCROLL,
            model.Size_object.MIDDLE,
            model.Position(1,2),
            model.Type_Characteristic.POWER
        )
        A.acquire_object(new_object)
        A.use_object(new_object)
        self.assertEqual(
            A.power,
            model.Settings.MIDDLE_CHARACTERISTIC + model.Size_object.MIDDLE.value,
        )
        self.assertEqual(len(A.backpack.scroll_list), 0)

    def test4(self):
        position = model.Position(0, 0)
        A = model.Character(position)
        new_object = model.Object(
            model.Type_Object.MEAL,
            model.Size_object.VERY_BIG,
            model.Position(3,3)
        )
        A.acquire_object(new_object)
        A.use_object(new_object)
        self.assertEqual(A.health, 90)
        A.acquire_object(new_object)
        A.use_object(new_object)
        self.assertEqual(A.health, 100)

    def test5(self):
        position_user = model.Position(0, 0)
        position_monster = model.Position(6, 3)
        user = model.Character(position_user)
        monster = model.Monster(Type_Monster.OGRE, position_monster)
        zone = monster.hostility // 10
        self.assertTrue(user.user_in_zone(position_monster, zone))
        monster.position.x += 1
        self.assertFalse(user.user_in_zone(position_monster, zone))


if __name__ == "__main__":
    unittest.main()
